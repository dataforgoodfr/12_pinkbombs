import test from 'node:test';
import assert from 'node:assert/strict';
import { schema, columnPayload, verifyColumn, NocoApi, bootstrap, apiInsertColumns } from './bootstrap.mjs';

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
  assert.ok(!apiInsertColumns.reponses_pinkometre.includes('empreinte_ip_hmac'));
  assert.ok(!apiInsertColumns.consommations.includes('id'));
});

test('only scenario and the response relation are required business fields', () => {
  assert.deepEqual(schema.tables.flatMap(table => table.columns.filter(column => column.required).map(column => column.title)), ['reponses_pinkometre_id', 'scenario']);
});

test('single selects preserve accents, commas, order and French labels', () => {
  const product = schema.tables[1].columns.find(column => column.title === 'produit');
  const payload = columnPayload(product);
  assert.equal(payload.colOptions.options[1].title, 'Sushis (makis, nigiris, sashimis)');
  assert.equal(payload.colOptions.options[2].title, 'Poké bowls');
  assert.equal(payload.colOptions.options[6].title, 'Quiche, sandwich, croque-monsieur');
  assert.equal(payload.colOptions.options[0].code, undefined);
  verifyColumn(payload, product);
  assert.throws(() => verifyColumn({ ...payload, colOptions: { options: [] } }, product), /incompatible select options/);
});

test('nullable fields have no required or unique declaration', () => {
  for (const name of ['email', 'empreinte_ip_hmac']) {
    const column = schema.tables[0].columns.find(candidate => candidate.title === name);
    const payload = columnPayload(column);
    assert.equal(payload.rqd, undefined);
    assert.equal(payload.unique, undefined);
    assert.throws(() => verifyColumn({ ...payload, unique: true }, column), /uniqueness is forbidden/);
  }
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
  await assert.rejects(api.login('private@example.invalid', 'secret'), /^Error: POST .*HTTP 401$/);
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