import { schema, physicalColumn, setting } from './noco-api.mjs';

export const apiInsertColumns = Object.fromEntries(schema.tables.map(table => [
  table.title, table.columns.filter(column => !column.generated).map(column => column.title),
]));

/**
 * Apply SQL constraints, decimal precision, and indexes to NocoDB-created tables.
 * Use the caller's transaction and metadata-derived names; never rename or drop columns.
 */
export async function provisionSchema(database, tables) {
  for (const definition of schema.tables) {
    const table = tables.get(definition.title);
    const namespace = table.base_id;
    const names = new Map(definition.columns.map(column => [column.title, physicalColumn(table, column)]));
    const relation = await database.raw('SELECT to_regclass(format(\'%I.%I\', ?::text, ?::text))::oid AS oid', [namespace, table.table_name]);
    const oid = relation.rows[0]?.oid;
    if (!oid) throw new Error(`${definition.title}: physical table is missing`);
    for (const column of definition.columns) {
      const name = names.get(column.title);
      if (column.required) await database.raw('ALTER TABLE ??.?? ALTER COLUMN ?? SET NOT NULL', [namespace, table.table_name, name]);
      if (column.uidt === 'Decimal') await database.raw('ALTER TABLE ??.?? ALTER COLUMN ?? TYPE numeric(30,10)', [namespace, table.table_name, name]);
      if (column.options) {
        const constraint = `pb_${table.id}_${column.title}_options`;
        const found = await database.raw('SELECT 1 FROM pg_constraint WHERE conrelid = ? AND conname = ?', [oid, constraint]);
        if (!found.rows.length) {
          const labels = schema.options[column.options].map(option => option.label);
          const quoted = await database.raw("SELECT string_agg(quote_literal(label), ', ' ORDER BY position) AS labels FROM unnest(?::text[]) WITH ORDINALITY AS options(label, position)", [labels]);
          await database.raw(`ALTER TABLE ??.?? ADD CONSTRAINT ?? CHECK (?? IN (${quoted.rows[0].labels}))`,
            [namespace, table.table_name, constraint, name]);
        }
      }
      if (column.references) {
        const parent = tables.get(column.references);
        const existing = await database.raw(`SELECT confrelid, conkey, confkey FROM pg_constraint
          WHERE contype = 'f' AND conrelid = ? AND conkey = ARRAY[(SELECT attnum FROM pg_attribute WHERE attrelid = ? AND attname = ?)]::smallint[]`, [oid, oid, name]);
        const target = await database.raw('SELECT to_regclass(format(\'%I.%I\', ?::text, ?::text))::oid AS oid', [parent.base_id, parent.table_name]);
        if (existing.rows.length && (existing.rows.length !== 1 || existing.rows[0].confrelid !== target.rows[0].oid)) throw new Error(`${name}: incompatible foreign key`);
        if (!existing.rows.length) await database.raw('ALTER TABLE ??.?? ADD CONSTRAINT ?? FOREIGN KEY (??) REFERENCES ??.?? (id)',
          [namespace, table.table_name, `pb_${table.id}_response_fk`, name, parent.base_id, parent.table_name]);
      }
    }
    for (const fields of definition.indexes) {
      const indexName = `pb_${table.id}_${fields.join('_')}`.slice(0, 63);
      await database.raw(`CREATE INDEX IF NOT EXISTS ?? ON ??.?? (${fields.map(() => '??').join(', ')})`,
        [indexName, namespace, table.table_name, ...fields.map(field => names.get(field))]);
      const index = await database.raw(`SELECT index.indisvalid, index.indisunique,
        array_agg(attribute.attname::text ORDER BY key.ordinality) AS columns
        FROM pg_index index JOIN pg_class object ON object.oid = index.indexrelid
        CROSS JOIN LATERAL unnest(index.indkey) WITH ORDINALITY AS key(attnum, ordinality)
        JOIN pg_attribute attribute ON attribute.attrelid = index.indrelid AND attribute.attnum = key.attnum
        WHERE index.indrelid = ? AND object.relname = ? GROUP BY index.indisvalid, index.indisunique`, [oid, indexName]);
      const actual = index.rows[0];
      if (!actual?.indisvalid || actual.indisunique || JSON.stringify(actual.columns) !== JSON.stringify(fields.map(field => names.get(field)))) throw new Error(`${indexName}: incompatible index`);
    }
    if (names.has('email')) {
      const unique = await database.raw(`SELECT 1 FROM pg_index index JOIN pg_attribute attribute
        ON attribute.attrelid = index.indrelid AND attribute.attnum = ANY(index.indkey)
        WHERE index.indrelid = ? AND index.indisunique AND attribute.attname = ?`, [oid, names.get('email')]);
      if (unique.rows.length) throw new Error('email must not have a unique index');
    }
  }
}

class AccessError extends Error {}

/** Return whether the role exists, rejecting privileged attributes, memberships, or ownership. */
async function inspectRole(transaction, username) {
  const result = await transaction.raw(`SELECT rolsuper, rolcreatedb, rolcreaterole, rolreplication, rolbypassrls,
    EXISTS (SELECT FROM pg_auth_members WHERE member = role.oid) AS membership,
    EXISTS (SELECT FROM pg_shdepend WHERE refclassid = 'pg_authid'::regclass AND refobjid = role.oid
      AND deptype = 'o' AND (dbid = 0 OR dbid = (SELECT oid FROM pg_database WHERE datname = current_database()))) AS owns_object
    FROM pg_roles role WHERE rolname = ?`, [username]);
  const role = result.rows[0];
  if (role && Object.values(role).some(Boolean)) throw new AccessError('API_DB_USER has administrative attributes, role memberships, or ownership; choose a dedicated role');
  return Boolean(role);
}

const privileges = {
  schema: ['USAGE', 'CREATE'], sequence: ['USAGE', 'SELECT', 'UPDATE'],
  table: ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'TRUNCATE', 'REFERENCES', 'TRIGGER', 'MAINTAIN'],
  column: ['SELECT', 'INSERT', 'UPDATE', 'REFERENCES'],
};

/** Check exact effective access, including PUBLIC grants, and forbid all grant options. */
async function verifyAccess(transaction, username, kind, oid, allowed, column) {
  for (const permission of privileges[kind]) {
    const parameters = column === undefined ? [username, oid] : [username, oid, column];
    const placeholders = column === undefined ? '?::name, ?::oid' : '?::name, ?::oid, ?::text';
    const query = `SELECT has_${kind}_privilege(${placeholders}, ?) AS permitted,
      has_${kind}_privilege(${placeholders}, ?) AS grantable`;
    const result = await transaction.raw(query, [...parameters, permission, ...parameters, `${permission} WITH GRANT OPTION`]);
    if (result.rows[0].permitted !== allowed.includes(permission) || result.rows[0].grantable) {
      throw new AccessError(`API_DB_USER has incompatible effective ${kind} privileges (${permission}); check PUBLIC grants`);
    }
  }
}

/** Revoke direct table/column grants without cascading; return the table OID and columns. */
async function resetTableAccess(transaction, namespace, name, username) {
  const result = await transaction.raw(`SELECT relation.oid, attribute.attname FROM pg_class relation
    JOIN pg_namespace namespace ON namespace.oid = relation.relnamespace
    JOIN pg_attribute attribute ON attribute.attrelid = relation.oid
    WHERE namespace.nspname = ? AND relation.relname = ? AND attribute.attnum > 0 AND NOT attribute.attisdropped`, [namespace, name]);
  if (!result.rows.length) throw new AccessError(`Missing API table ${name}`);
  const columns = result.rows.map(row => row.attname);
  await transaction.raw('REVOKE ALL ON TABLE ??.?? FROM ?? RESTRICT', [namespace, name, username]);
  for (const permission of privileges.column) {
    await transaction.raw(`REVOKE ${permission} (${columns.map(() => '??').join(', ')}) ON TABLE ??.?? FROM ?? RESTRICT`, [...columns, namespace, name, username]);
  }
  return { oid: result.rows[0].oid, columns };
}

/**
 * Configure API_DB_USER, its password, retry storage, and least-privilege grants.
 * Serialize changes by role and roll them back together if verification fails.
 * Called only during initialization or explicit maintenance, not unchanged-base startup.
 */
export async function provisionApiDatabase(database, tables, environment) {
  const username = setting(environment, 'API_DB_USER');
  const password = setting(environment, 'API_DB_PASSWORD');
  if (!/^[A-Za-z_][A-Za-z0-9_]{0,62}$/.test(username) || username === 'pinkbombs') throw new Error('API_DB_USER must be a separate, valid PostgreSQL role name');
  const namespace = tables.get('reponses_pinkometre')?.base_id;
  if (!namespace || !/^[A-Za-z0-9_]+$/.test(namespace)) throw new Error('NocoDB base schema is unavailable');
  try {
    await database.transaction(async transaction => {
      await transaction.raw('SELECT pg_advisory_xact_lock(hashtext(?))', [`pinkbombs:api:${username}`]);
      const exists = await inspectRole(transaction, username);
      const role = await transaction.raw('SELECT format(?::text, ?::text, ?::text) AS sql', [
        `${exists ? 'ALTER' : 'CREATE'} ROLE %I LOGIN PASSWORD %L NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOREPLICATION NOBYPASSRLS`, username, password,
      ]);
      await transaction.raw(role.rows[0].sql);
      await transaction.raw('CREATE SCHEMA IF NOT EXISTS pinkbombs_api AUTHORIZATION pinkbombs');
      await transaction.raw(`CREATE TABLE IF NOT EXISTS pinkbombs_api.idempotency_keys (
        key_hash varchar(64) PRIMARY KEY, request_hash varchar(64) NOT NULL,
        response_id bigint NOT NULL, created_at timestamptz NOT NULL DEFAULT now())`);
      await transaction.raw('CREATE INDEX IF NOT EXISTS pb_idempotency_created_at_idx ON pinkbombs_api.idempotency_keys (created_at)');
      for (const name of [namespace, 'pinkbombs_api']) {
        const result = await transaction.raw('SELECT oid FROM pg_namespace WHERE nspname = ?', [name]);
        if (!result.rows.length) throw new AccessError('Missing API schema');
        await transaction.raw('REVOKE ALL ON SCHEMA ?? FROM ?? RESTRICT', [name, username]);
        await transaction.raw('GRANT USAGE ON SCHEMA ?? TO ??', [name, username]);
        await verifyAccess(transaction, username, 'schema', result.rows[0].oid, ['USAGE']);
      }
      const keys = await resetTableAccess(transaction, 'pinkbombs_api', 'idempotency_keys', username);
      await transaction.raw('GRANT SELECT, INSERT, DELETE ON pinkbombs_api.idempotency_keys TO ??', [username]);
      await verifyAccess(transaction, username, 'table', keys.oid, ['SELECT', 'INSERT', 'DELETE']);
      for (const column of keys.columns) await verifyAccess(transaction, username, 'column', keys.oid, ['SELECT', 'INSERT'], column);
      for (const definition of schema.tables) {
        const table = tables.get(definition.title);
        if (table?.base_id !== namespace) throw new AccessError('API tables must belong to the same base');
        const physical = await resetTableAccess(transaction, namespace, table.table_name, username);
        const inserted = definition.columns.filter(column => !column.generated).map(column => physicalColumn(table, column));
        const primaryKey = physicalColumn(table, definition.columns.find(column => column.generated));
        await transaction.raw(`GRANT INSERT (${inserted.map(() => '??').join(', ')}) ON ??.?? TO ??`, [...inserted, namespace, table.table_name, username]);
        await transaction.raw('GRANT SELECT (??) ON ??.?? TO ??', [primaryKey, namespace, table.table_name, username]);
        const result = await transaction.raw(`SELECT sequence.oid, namespace.nspname, sequence.relname
          FROM pg_class sequence JOIN pg_namespace namespace ON namespace.oid = sequence.relnamespace
          WHERE sequence.oid = pg_get_serial_sequence(format('%I.%I', ?::text, ?::text), ?)::regclass`, [namespace, table.table_name, primaryKey]);
        const sequence = result.rows[0];
        if (!sequence) throw new AccessError(`${definition.title}: generated ID sequence is unavailable`);
        await transaction.raw('REVOKE ALL ON SEQUENCE ??.?? FROM ?? RESTRICT', [sequence.nspname, sequence.relname, username]);
        await transaction.raw('GRANT USAGE ON SEQUENCE ??.?? TO ??', [sequence.nspname, sequence.relname, username]);
        await verifyAccess(transaction, username, 'sequence', sequence.oid, ['USAGE']);
        await verifyAccess(transaction, username, 'table', physical.oid, []);
        for (const column of physical.columns) {
          const allowed = [];
          if (inserted.includes(column)) allowed.push('INSERT');
          if (column === primaryKey) allowed.push('SELECT');
          await verifyAccess(transaction, username, 'column', physical.oid, allowed, column);
        }
      }
      await inspectRole(transaction, username);
      await transaction.raw('ALTER ROLE ?? SET search_path = ??, pinkbombs_api', [username, namespace]);
    });
  } catch (error) {
    if (error instanceof AccessError) throw error;
    throw new Error('API database provisioning rolled back; check dependent grants, schema and database logs');
  }
}