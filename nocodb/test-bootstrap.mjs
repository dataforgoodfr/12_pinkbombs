import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, copyFile, readFile, stat, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { execFileSync } from 'node:child_process';
import { schema, columnPayload, physicalColumn, verifyTables, checkRecords, NocoApi } from './noco-api.mjs';
import { bootstrap, findBase } from './bootstrap.mjs';
import { apiInsertColumns, provisionApiDatabase, provisionSchema } from './provision.mjs';

test('option constraint checks fail closed on definition, validation state, and kind', async () => {
  const expected = 'CHECK (impact_initial = ANY (ARRAY[expected labels]))';
  for (const actual of [
    { contype: 'c', convalidated: true, definition: 'CHECK (true)' },
    { contype: 'c', convalidated: false, definition: expected },
    { contype: 'u', convalidated: true, definition: expected },
  ]) {
    const statements = [];
    const database = { raw: async statement => {
      statements.push(statement);
      if (statement.includes('SELECT to_regclass')) return { rows: [{ oid: 1 }] };
      if (statement.includes('SELECT contype')) return { rows: [actual] };
      if (statement.includes('string_agg')) return { rows: [{ labels: "'expected labels'" }] };
      if (statement.includes('SELECT pg_get_constraintdef')) return { rows: [{ definition: expected }] };
      return { rows: [] };
    } };
    const definition = schema.tables[0];
    const table = { id: 'responses', title: definition.title, table_name: definition.title, base_id: 'base', columns: definition.columns.map(columnPayload) };
    await assert.rejects(provisionSchema(database, new Map([[definition.title, table]])), /incompatible option constraint.*validated CHECK/);
    assert.ok(!statements.some(statement => /DROP CONSTRAINT/.test(statement)));
  }
});

test('unsafe existing API roles are rejected before password or ACL mutations', async () => {
  for (const property of ['rolsuper', 'rolcreatedb', 'rolcreaterole', 'rolreplication', 'rolbypassrls', 'memberships', 'ownership']) {
    const statements = [];
    const transaction = {
      raw: async statement => {
        statements.push(statement);
        return { rows: statement.includes('FROM pg_roles role') ? [{ [property]: true }] : [] };
      },
    };
    const database = { transaction: callback => callback(transaction) };
    const tables = new Map([
      ['reponses_pinkometre', { base_id: 'base' }], ['consommations', {}],
    ]);
    await assert.rejects(provisionApiDatabase(database, tables, {
      API_DB_USER: 'api_test', API_DB_PASSWORD: 'private-password',
    }), /administrative attributes, role memberships, or ownership/);
    assert.equal(statements.length, 2);
    assert.ok(statements.every(statement => !statement.includes('private-password')));
  }
});

test('all frontend options have stable unique codes and existing French labels', () => {
  for (const options of Object.values(schema.options)) {
    const codes = options.map(option => option.code);
    assert.ok(codes.every(Boolean));
    assert.equal(new Set(codes).size, codes.length);
    assert.ok(options.every(option => option.label));
  }
  assert.deepEqual(schema.options.scenarios.map(option => option.label), ['Initiale', 'Après engagement']);
  assert.deepEqual(schema.options.unites.map(option => option.code), ['portion', 'piece', 'slice']);
});

test('API database role only receives approved submission insert columns', () => {
  assert.deepEqual(apiInsertColumns.reponses_pinkometre, [
    'email', 'impact_initial', 'impact_apres_engagement', 'alternative_choisie',
    'supplement_choisi', 'consentement_omega3',
  ]);
  assert.ok(!apiInsertColumns.consommations.includes('id'));
  assert.equal(apiInsertColumns.consommations[0], 'reponse_pinkometre');
  assert.equal(schema.tables[1].columns.find(column => column.references).physicalName, undefined);
  assert.ok(!schema.tables[0].columns.some(column => column.title === 'empreinte_ip_hmac'));
  assert.deepEqual(schema.tables[0].indexes, []);
  assert.deepEqual(schema.tables[1].indexes, [['reponse_pinkometre'], ['scenario'], ['produit']]);
});

test('only scenario and the response relation are required business fields', () => {
  assert.deepEqual(schema.tables.flatMap(table => table.columns.filter(column => column.required).map(column => column.title)), ['reponse_pinkometre', 'scenario']);
});

test('single selects preserve accents, commas, order and French labels', () => {
  const product = schema.tables[1].columns.find(column => column.title === 'produit');
  const payload = columnPayload(product);
  assert.equal(payload.colOptions.options[1].title, 'Sushis (makis, nigiris, sashimis)');
  assert.equal(payload.colOptions.options[2].title, 'Poké bowls');
  assert.equal(payload.colOptions.options[6].title, 'Quiche, sandwich, croque-monsieur');
  assert.equal(payload.colOptions.options[0].code, undefined);
  assert.equal(payload.uidt, 'SingleSelect');
});

test('no-salmon product uses the literal null code', () => {
  const noSalmon = schema.options.produits.find(option => option.code === 'null');
  assert.deepEqual(noSalmon, { label: 'Je ne consomme pas de saumon', code: 'null' });
});

test('email is nullable and non-unique', () => {
  const column = schema.tables[0].columns.find(candidate => candidate.title === 'email');
  const payload = columnPayload(column);
  assert.equal(payload.rqd, undefined);
  assert.equal(payload.unique, undefined);
});

test('custom frequency annual counts stay decimal and canonical names stay unchanged', () => {
  const columns = schema.tables[1].columns;
  assert.equal(columns.find(column => column.title === 'occurence_par_an').uidt, 'Decimal');
  assert.equal(columns.find(column => column.title === 'frequence').options, 'frequences');
  assert.equal(schema.options.frequences.length, 9);
  assert.equal(columns.find(column => column.title === 'variante').required, undefined);
});

test('missing credentials fail before network or database access', async () => {
  await assert.rejects(bootstrap({}), /NOCODB_BOOTSTRAP_EMAIL/);
});

test('API failures do not expose response bodies or credentials', async () => {
  const api = new NocoApi('http://localhost', async () => ({ ok: false, status: 401 }));
  await assert.rejects(api.login('private@example.invalid', 'secret'), /^Error: NocoDB POST .*HTTP 401/);
});

test('metadata listing follows pagination', async () => {
  let calls = 0;
  const api = new NocoApi('http://localhost', async () => ({ ok: true, status: 200, json: async () => (++calls === 1 ? { list: [{ id: 1 }], pageInfo: { isLastPage: false } } : { list: [{ id: 2 }], pageInfo: { isLastPage: true } }) }));
  assert.deepEqual(await api.list('/tables'), [{ id: 1 }, { id: 2 }]);
});

test('member listing unwraps the users page without changing permissions', async () => {
  const api = new NocoApi('http://localhost', async () => ({ ok: true, status: 200, json: async () => ({ users: { list: [{ id: 'member', roles: 'viewer' }], pageInfo: { isLastPage: true } } }) }));
  assert.deepEqual(await api.list('/members'), [{ id: 'member', roles: 'viewer' }]);
});

const environment = { NOCODB_BOOTSTRAP_EMAIL: 'admin@example.invalid', NOCODB_BOOTSTRAP_PASSWORD: 'private' };

function existingInstallation(bases = [{ id: 'base', title: schema.base }]) {
  const calls = [];
  const api = {
    login: async () => {},
    request: async (method, path) => {
      calls.push({ method, path });
      if (path.endsWith('/info')) return { firstUser: false };
      throw new Error('Unexpected metadata access');
    },
    list: async () => bases,
  };
  const statements = [];
  const database = { transaction: callback => callback({ raw: async sql => { statements.push(sql); return { rows: [] }; } }) };
  return { api, database, calls, statements };
}

test('existing bases, even incomplete ones, are untouched on ordinary startup', async () => {
  const fixture = existingInstallation();
  const result = await bootstrap(environment, { ...fixture, mode: 'start' });
  assert.equal(result.status, 'existing');
  assert.ok(fixture.calls.every(call => call.method === 'GET'));
  assert.equal(fixture.statements.length, 1);
  assert.match(fixture.statements[0], /pg_advisory_xact_lock/);
});

test('duplicate base names fail before schema changes', async () => {
  const fixture = existingInstallation([{ title: schema.base }, { title: schema.base }]);
  await assert.rejects(bootstrap(environment, { ...fixture, mode: 'start' }), /Multiple bases/);
  assert.ok(fixture.calls.every(call => call.method === 'GET'));
});

test('maintenance never creates an absent base', async () => {
  for (const mode of ['resume', 'provision']) {
    const fixture = existingInstallation([]);
    await assert.rejects(bootstrap(environment, { ...fixture, mode }), /missing/);
    assert.ok(fixture.calls.every(call => call.method === 'GET'));
  }
});

test('new installations require API settings before creating a base', async () => {
  const fixture = existingInstallation([]);
  await assert.rejects(bootstrap(environment, { ...fixture, mode: 'start' }), /API_DB_USER/);
  assert.ok(fixture.calls.every(call => call.method === 'GET'));
});

test('unknown commands fail without accessing NocoDB', async () => {
  await assert.rejects(bootstrap({}, { mode: 'reset' }), /Usage/);
});

test('base lookup honors configured names', async () => {
  const fixture = existingInstallation([{ title: 'staging', id: 'staging-id' }]);
  assert.equal((await findBase(fixture.api, 'staging')).id, 'staging-id');
});

test('relation physical names come from metadata, never a hardcoded rename', () => {
  const relation = schema.tables[1].columns.find(column => column.references);
  for (const name of ['reponses_pinkometre_id', 'reponses_pinkometre_fk', 'generated_123']) {
    const table = { columns: [
      { title: relation.title, colOptions: { type: 'bt', fk_child_column_id: 'fk' } },
      { id: 'fk', column_name: name },
    ] };
    assert.equal(physicalColumn(table, relation), name);
    table.columns.pop();
    assert.throws(() => physicalColumn(table, relation), /physical column/);
  }
});

test('table verification rejects select drift rather than rewriting options', () => {
  const tables = new Map(schema.tables.map(definition => [definition.title, {
    title: definition.title, table_name: definition.title, id: definition.title,
    columns: definition.columns.map(column => ({ ...columnPayload(column), id: column.title })),
  }]));
  const product = tables.get('consommations').columns.find(column => column.title === 'produit');
  const link = tables.get('consommations').columns.find(column => column.title === 'reponse_pinkometre');
  link.colOptions = { type: 'bt', fk_child_column_id: 'fk', fk_related_model_id: 'reponses_pinkometre' };
  tables.get('consommations').columns.push({ id: 'fk', column_name: 'generated_fk' });
  product.colOptions.options = [];
  assert.throws(() => verifyTables(tables), /incompatible select options/);
});

test('empty non-final pagination pages fail rather than loop forever', async () => {
  const api = new NocoApi('http://test', async () => ({ ok: true, status: 200, json: async () => ({ list: [], pageInfo: { isLastPage: false } }) }));
  await assert.rejects(api.list('/tables'), /Empty NocoDB pagination/);
});

test('diagnostics exercise the UI grid, not just the records API', async () => {
  const api = {
    list: async () => [{ id: 'grid', type: 3, show: true }],
    request: async (method, path) => {
      if (path.includes('/views/')) throw new Error('broken grid relation');
      return { list: [] };
    },
  };
  await assert.rejects(checkRecords(api, new Map([['table', { id: 'table', base_id: 'base' }]])), /broken grid relation/);
});

test('setup generates private secrets once and preserves all existing values', async () => {
  const directory = await mkdtemp(join(tmpdir(), 'pinkbombs-setup-'));
  try {
    for (const file of ['setup.sh', '.env.example']) await copyFile(new URL(file, import.meta.url), join(directory, file));
    execFileSync('bash', [join(directory, 'setup.sh')]);
    const original = await readFile(join(directory, '.env'), 'utf8');
    assert.ok(!original.includes('GENERATE_'));
    assert.equal((await stat(join(directory, '.env'))).mode & 0o777, 0o600);
    execFileSync('bash', [join(directory, 'setup.sh')]);
    assert.equal(await readFile(join(directory, '.env'), 'utf8'), original);
  } finally {
    await rm(directory, { recursive: true, force: true });
  }
});

test('failed first-install record verification leaves no completion marker or SQL changes', async () => {
  const fixture = existingInstallation([]);
  const metadata = new Map();
  const writes = [];
  fixture.api.list = async path => {
    if (path === '/api/v2/meta/bases/') return [];
    return [...metadata.values()];
  };
  fixture.api.request = async (method, path, value) => {
    if (method !== 'GET') writes.push({ method, path, value });
    if (path.endsWith('/info')) return { firstUser: false };
    if (path === '/api/v2/meta/bases/') return { id: 'base' };
    if (method === 'POST' && path.endsWith('/tables')) {
      const table = { ...value, id: value.title, base_id: 'base', columns: value.columns.map(column => ({ ...column, id: column.title })) };
      metadata.set(table.id, table);
      return table;
    }
    if (method === 'POST' && path.endsWith('/columns')) {
      metadata.get('consommations').columns.push(
        { ...value, colOptions: { type: 'bt', fk_child_column_id: 'fk', fk_related_model_id: 'reponses_pinkometre' } },
        { id: 'fk', column_name: 'reponses_pinkometre_id' },
      );
      return {};
    }
    if (path.includes('/records')) throw new Error('records are unreadable');
    return metadata.get(path.split('/').at(-1));
  };
  await assert.rejects(bootstrap({ ...environment, API_DB_USER: 'dedicated', API_DB_PASSWORD: 'private' }, { ...fixture, mode: 'start' }), /records are unreadable/);
  assert.equal(fixture.statements.length, 1);
  assert.equal(writes.filter(call => call.path.endsWith('/tables')).length, 2);
  assert.equal(writes.filter(call => call.path.endsWith('/columns')).length, 1);
  assert.ok(writes.every(call => call.method === 'POST'));
});