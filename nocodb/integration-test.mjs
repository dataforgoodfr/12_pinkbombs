/** Read-only diagnostic: verify schema metadata, records/UI grids, and setup completion. */
import assert from 'node:assert/strict';
import { NocoApi, schema, readTables, verifyTables, checkRecords } from './noco-api.mjs';
import { authenticate, connectDatabase, findBase } from './bootstrap.mjs';

const environment = process.env;
const baseTitle = environment.NOCODB_BASE_NAME || schema.base;
const admin = new NocoApi(environment.NOCODB_API_URL || 'http://nocodb:8080');

await authenticate(admin, environment);
const base = await findBase(admin, baseTitle);
assert.ok(base, `Base ${baseTitle} is unavailable`);

const tables = await readTables(admin, base.id);
verifyTables(tables);
await checkRecords(admin, tables);
const database = connectDatabase(environment);
try {
  const installed = await database.raw("SELECT to_regclass('pinkbombs_api.installation') AS table_name");
  if (!installed.rows[0].table_name) throw new Error('Installation has not completed; review the base and explicitly resume initialization');
  const completion = await database('installation').withSchema('pinkbombs_api').where({ base_id: base.id }).first();
  assert.ok(completion, 'This base has no completed initialization; review before running resume');
} finally {
  await database.destroy();
}
console.log('PASS: schema metadata matches, both NocoDB tables are readable, and initialization completed. No data was modified.');
