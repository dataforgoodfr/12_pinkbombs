import test from 'node:test';
import assert from 'node:assert/strict';
import { randomUUID } from 'node:crypto';
import { createRequire } from 'node:module';
import { schema, provisionApiDatabase } from './bootstrap.mjs';

test('provisioned API role enforces PostgreSQL privileges', { skip: !process.env.TEST_DATABASE_URL }, async context => {
  const connection = process.env.TEST_DATABASE_URL;
  assert.match(new URL(connection).pathname, /^\/test_[a-zA-Z0-9_]+$/,
    'TEST_DATABASE_URL must point to a disposable test_* database');
  let runtimeRequire = createRequire(import.meta.url);
  try {
    runtimeRequire.resolve('knex');
  } catch {
    runtimeRequire = createRequire('/usr/src/app/package.json');
  }
  const database = runtimeRequire('knex')({ client: 'pg', connection, pool: { min: 0, max: 1 } });

  async function fixture(callback) {
    const rollback = new Error('rollback disposable fixture');
    try {
      await database.transaction(async transaction => {
        const guard = await transaction.raw("SELECT current_database() AS database, current_setting('server_version_num')::integer AS version, to_regnamespace('pinkbombs_api') AS existing");
        assert.match(guard.rows[0].database, /^test_/);
        assert.ok(guard.rows[0].version >= 170000, 'PostgreSQL 17 or later is required');
        assert.equal(guard.rows[0].existing, null, 'Refusing to use an existing pinkbombs_api schema');
        const owner = await transaction.raw("SELECT 1 FROM pg_roles WHERE rolname = 'pinkbombs'");
        if (!owner.rows.length) await transaction.raw('CREATE ROLE pinkbombs');
        const suffix = randomUUID().replaceAll('-', '');
        const baseSchema = `pb_test_${suffix}`;
        const username = `pb_api_${suffix}`;
        const environment = { API_DB_USER: username, API_DB_PASSWORD: 'disposable-password' };
        await transaction.raw('CREATE SCHEMA ??', [baseSchema]);
        const tables = new Map();
        for (const definition of schema.tables) {
          const columns = definition.columns.map(column => ({
            ...column,
            id: column.title,
            column_name: column.uidt === 'CreatedTime' ? 'created_at' : column.title,
            pk: !!column.generated,
            system: column.uidt === 'CreatedTime',
            ...(column.references ? { colOptions: { fk_child_column_id: 'response_fk' } } : {}),
          }));
          if (definition.title === 'consommations') {
            columns.push({ id: 'response_fk', title: 'response_fk', column_name: 'reponses_pinkometre_fk' });
          }
          const tableName = `${definition.title}_Mixed`;
          await transaction.schema.withSchema(baseSchema).createTable(tableName, builder => {
            builder.increments('id');
            for (const column of columns.filter(candidate => !candidate.generated && !candidate.references)) {
              if (column.uidt === 'CreatedTime') builder.timestamp(column.column_name).defaultTo(transaction.fn.now());
              else builder.text(column.column_name);
            }
            if (definition.title === 'reponses_pinkometre') builder.timestamp('created_at').defaultTo(transaction.fn.now());
            builder.text('unexpected');
          });
          tables.set(definition.title, { base_id: baseSchema, table_name: tableName, columns });
        }
        const response = [baseSchema, tables.get('reponses_pinkometre').table_name];
        const consumption = [baseSchema, tables.get('consommations').table_name];
        const provision = (password = environment.API_DB_PASSWORD) => provisionApiDatabase(transaction, tables, { ...environment, API_DB_PASSWORD: password });
        const asApi = (statement, bindings = []) => transaction.transaction(async session => {
          await session.raw('SET LOCAL SESSION AUTHORIZATION ??', [username]);
          const result = await session.raw(statement, bindings);
          await session.raw('RESET SESSION AUTHORIZATION');
          return result;
        });
        await callback({ transaction, username, baseSchema, response, consumption, provision, asApi });
        throw rollback;
      });
    } catch (error) {
      if (error !== rollback) throw error;
    }
  }

  try {
    await context.test('expiry index is created, reused and restored on an existing idempotency table', () => fixture(async ({ transaction, provision }) => {
      const readExpiryIndex = () => transaction.raw(`
        SELECT index_record.indexrelid::text AS oid, index_record.indisvalid AS valid,
          index_record.indisready AS ready, index_record.indisunique AS unique,
          index_record.indnatts AS columns, attribute.attname AS column,
          access_method.amname AS method, index_record.indpred AS predicate,
          index_record.indexprs AS expressions
        FROM pg_index index_record
        JOIN pg_class index_relation ON index_relation.oid = index_record.indexrelid
        JOIN pg_am access_method ON access_method.oid = index_relation.relam
        JOIN pg_attribute attribute ON attribute.attrelid = index_record.indrelid
          AND attribute.attnum = index_record.indkey[0]
        WHERE index_record.indrelid = 'pinkbombs_api.idempotency_keys'::regclass
          AND index_relation.relname = 'pb_idempotency_created_at_idx'`);
      await provision();
      const created = await readExpiryIndex();
      assert.equal(created.rows.length, 1);
      const { oid, ...definition } = created.rows[0];
      assert.deepEqual(definition, {
        valid: true, ready: true, unique: false, columns: 1, column: 'created_at',
        method: 'btree', predicate: null, expressions: null,
      });
      await provision();
      assert.deepEqual((await readExpiryIndex()).rows, created.rows);
      await transaction.raw('DROP INDEX pinkbombs_api.pb_idempotency_created_at_idx');
      await provision();
      const restored = await readExpiryIndex();
      assert.equal(restored.rows.length, 1);
      assert.notEqual(restored.rows[0].oid, oid);
      assert.deepEqual({ ...restored.rows[0], oid }, created.rows[0]);
    }));

    await context.test('fresh creation, reuse and password rotation preserve permitted operations', () => fixture(async ({ transaction, username, response, consumption, provision, asApi }) => {
      await provision();
      const original = await transaction.raw('SELECT rolpassword FROM pg_authid WHERE rolname = ?', [username]);
      await provision("rotated-'?\\-password");
      const rotated = await transaction.raw('SELECT rolpassword FROM pg_authid WHERE rolname = ?', [username]);
      assert.notEqual(original.rows[0].rolpassword, rotated.rows[0].rolpassword);
      await transaction.schema.withSchema(response[0]).createTable('unrelated', builder => builder.integer('id'));
      await transaction.raw('GRANT SELECT ON TABLE ??.unrelated TO ??', [response[0], username]);
      await provision();
      await asApi('SELECT * FROM ??.unrelated', [response[0]]);
      const inserted = await asApi('INSERT INTO ??.?? (email) VALUES (?) RETURNING id', [...response, 'example@example.invalid']);
      await asApi('INSERT INTO ??.?? (scenario, reponses_pinkometre_fk) VALUES (?, ?) RETURNING id', [...consumption, 'Initiale', inserted.rows[0].id]);
      await asApi("INSERT INTO pinkbombs_api.idempotency_keys (key_hash, request_hash, response_id) VALUES ('key', 'request', ?)", [inserted.rows[0].id]);
      assert.equal((await asApi('SELECT * FROM pinkbombs_api.idempotency_keys')).rows.length, 1);
      await asApi("DELETE FROM pinkbombs_api.idempotency_keys WHERE key_hash = 'key'");
      for (const table of [response, consumption]) {
        for (const statement of ['SELECT * FROM ??.??', 'UPDATE ??.?? SET id = 1', 'DELETE FROM ??.??', 'TRUNCATE ??.??', 'INSERT INTO ??.?? (id) VALUES (999)', "INSERT INTO ??.?? (unexpected) VALUES ('bad')"]) {
          await assert.rejects(asApi(statement, table), { code: '42501' });
        }
      }
      await assert.rejects(asApi('INSERT INTO ??.?? (created_at) VALUES (now())', response), { code: '42501' });
      await assert.rejects(asApi('UPDATE pinkbombs_api.idempotency_keys SET response_id = 1'), { code: '42501' });
      await assert.rejects(asApi('SET ROLE pinkbombs'), { code: '42501' });
      await assert.rejects(asApi('CREATE TABLE pinkbombs_api.forbidden (id integer)'), { code: '42501' });
    }));

    await context.test('excess direct table, column, schema and sequence grants are removed', () => fixture(async ({ transaction, username, baseSchema, response, consumption, provision, asApi }) => {
      await provision();
      for (const table of [response, consumption]) {
        await transaction.raw('GRANT ALL PRIVILEGES ON TABLE ??.?? TO ?? WITH GRANT OPTION', [...table, username]);
        await transaction.raw('GRANT SELECT (unexpected), INSERT (id), UPDATE (unexpected), REFERENCES (id) ON TABLE ??.?? TO ?? WITH GRANT OPTION', [...table, username]);
      }
      await transaction.raw('GRANT ALL PRIVILEGES ON SCHEMA ?? TO ?? WITH GRANT OPTION', [baseSchema, username]);
      await transaction.raw('GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA ?? TO ?? WITH GRANT OPTION', [baseSchema, username]);
      await transaction.raw('GRANT UPDATE (response_id) ON pinkbombs_api.idempotency_keys TO ?? WITH GRANT OPTION', [username]);
      await provision();
      await assert.rejects(asApi('SELECT unexpected FROM ??.??', response), { code: '42501' });
      const sequence = await transaction.raw("SELECT pg_get_serial_sequence(format('%I.%I', ?::text, ?::text), 'id') AS name", response);
      await assert.rejects(asApi('SELECT setval(?::regclass, 100)', [sequence.rows[0].name]), { code: '42501' });
      const identifier = await transaction.raw('SELECT relname FROM pg_class WHERE oid = ?::regclass', [sequence.rows[0].name]);
      await assert.rejects(asApi('SELECT * FROM ??.??', [baseSchema, identifier.rows[0].relname]), { code: '42501' });
    }));

    for (const alteration of ['SUPERUSER', 'CREATEDB', 'CREATEROLE', 'REPLICATION', 'BYPASSRLS', 'MEMBERSHIP', 'OWNERSHIP', 'DATABASE OWNERSHIP']) {
      await context.test(`rejects ${alteration} without changing the existing identity`, () => fixture(async ({ transaction, username, response, provision }) => {
        await provision();
        if (alteration === 'MEMBERSHIP') {
          await transaction.raw('GRANT pinkbombs TO ?? WITH INHERIT FALSE, SET TRUE', [username]);
        } else if (alteration === 'OWNERSHIP') {
          await transaction.raw('ALTER TABLE ??.?? OWNER TO ??', [...response, username]);
        } else if (alteration === 'DATABASE OWNERSHIP') {
          const current = await transaction.raw('SELECT current_database() AS name');
          await transaction.raw('ALTER DATABASE ?? OWNER TO ??', [current.rows[0].name, username]);
        } else {
          await transaction.raw(`ALTER ROLE ?? ${alteration}`, [username]);
        }
        const before = await transaction.raw('SELECT * FROM pg_authid WHERE rolname = ?', [username]);
        await assert.rejects(provision('must-not-be-applied'), /administrative attributes, role memberships, or ownership/);
        assert.deepEqual((await transaction.raw('SELECT * FROM pg_authid WHERE rolname = ?', [username])).rows, before.rows);
      }));
    }

    for (const access of ['table', 'column', 'schema', 'sequence', 'idempotency']) {
      await context.test(`rejects effective PUBLIC ${access} access and rolls back direct revocations`, () => fixture(async ({ transaction, username, baseSchema, response, provision }) => {
        await provision();
        await transaction.raw('GRANT DELETE ON TABLE ??.?? TO ??', [...response, username]);
        if (access === 'table') await transaction.raw('GRANT SELECT ON TABLE ??.?? TO PUBLIC', response);
        if (access === 'column') await transaction.raw('GRANT UPDATE (unexpected) ON TABLE ??.?? TO PUBLIC', response);
        if (access === 'schema') await transaction.raw('GRANT CREATE ON SCHEMA ?? TO PUBLIC', [baseSchema]);
        if (access === 'sequence') await transaction.raw('GRANT UPDATE ON ALL SEQUENCES IN SCHEMA ?? TO PUBLIC', [baseSchema]);
        if (access === 'idempotency') await transaction.raw('GRANT UPDATE (response_id) ON pinkbombs_api.idempotency_keys TO PUBLIC');
        const before = await transaction.raw('SELECT rolpassword FROM pg_authid WHERE rolname = ?', [username]);
        await assert.rejects(provision('must-not-be-applied'), /incompatible effective/);
        assert.deepEqual((await transaction.raw('SELECT rolpassword FROM pg_authid WHERE rolname = ?', [username])).rows, before.rows);
        const retained = await transaction.raw("SELECT has_table_privilege(?::name, format('%I.%I', ?::text, ?::text), 'DELETE') AS access", [username, ...response]);
        assert.equal(retained.rows[0].access, true);
      }));
    }

    await context.test('failed first-time provisioning leaves no API role or idempotency schema', () => fixture(async ({ transaction, username, response, provision }) => {
      await transaction.raw('GRANT SELECT ON TABLE ??.?? TO PUBLIC', response);
      await assert.rejects(provision(), /incompatible effective/);
      assert.equal((await transaction.raw('SELECT 1 FROM pg_roles WHERE rolname = ?', [username])).rows.length, 0);
      assert.equal((await transaction.raw("SELECT to_regnamespace('pinkbombs_api') AS namespace")).rows[0].namespace, null);
    }));

    await context.test('dependent grants fail safely without cascading or leaking credentials', () => fixture(async ({ transaction, username, response, provision }) => {
      await provision();
      const recipient = `${username}_reader`;
      await transaction.raw('CREATE ROLE ??', [recipient]);
      await transaction.raw('GRANT SELECT ON TABLE ??.?? TO ?? WITH GRANT OPTION', [...response, username]);
      await transaction.raw('SET LOCAL ROLE ??', [username]);
      await transaction.raw('GRANT SELECT ON TABLE ??.?? TO ??', [...response, recipient]);
      await transaction.raw('RESET ROLE');
      await assert.rejects(provision('private-must-not-leak'), error => {
        assert.match(error.message, /rolled back/);
        assert.ok(!error.message.includes('private-must-not-leak'));
        return true;
      });
      const retained = await transaction.raw("SELECT has_table_privilege(?::name, format('%I.%I', ?::text, ?::text), 'SELECT') AS access", [recipient, ...response]);
      assert.equal(retained.rows[0].access, true);
    }));
  } finally {
    await database.destroy();
  }
});