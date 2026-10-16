import { createRequire } from 'node:module';
import { pathToFileURL } from 'node:url';
import { NocoApi, schema, setting, columnPayload, readTables, verifyTables, checkRecords } from './noco-api.mjs';
import { provisionSchema, provisionApiDatabase } from './provision.mjs';

/** Open the administrator SQL pool for initialization; the caller must destroy it. */
export function connectDatabase(environment) {
  let require = createRequire(import.meta.url);
  try { require.resolve('knex'); } catch { require = createRequire('/usr/src/app/package.json'); }
  return require('knex')({
    client: 'pg',
    connection: {
      host: environment.PGHOST || 'db', port: Number(environment.PGPORT || 5432),
      database: environment.PGDATABASE || 'pinkbombs', user: 'pinkbombs',
      password: setting(environment, 'POSTGRES_PASSWORD'),
    },
    pool: { min: 0, max: 1 },
  });
}

/** Authenticate the NocoDB administrator, allowing first-account signup only when requested. */
export async function authenticate(api, environment, allowSignup = false) {
  const email = setting(environment, 'NOCODB_BOOTSTRAP_EMAIL');
  const password = setting(environment, 'NOCODB_BOOTSTRAP_PASSWORD');
  const info = await api.request('GET', '/api/v1/db/meta/nocodb/info');
  if (info.firstUser && !allowSignup) throw new Error('No NocoDB administrator exists; run start.sh first');
  await api.login(email, password, info.firstUser === true);
}

/** Return the base matching a unique title, or undefined if absent; never modify bases. */
export async function findBase(api, title) {
  const matches = (await api.list('/api/v2/meta/bases/')).filter(base => base.title === title);
  if (matches.length > 1) throw new Error(`Multiple bases named ${title}; choose a unique NOCODB_BASE_NAME`);
  return matches[0];
}

/** Create missing tables and relations through NocoDB, then return refreshed metadata. */
async function createTables(api, base) {
  const available = await api.list(`/api/v2/meta/bases/${base.id}/tables`);
  for (const definition of schema.tables) {
    const matches = available.filter(table => table.title === definition.title);
    if (matches.length > 1) throw new Error(`Ambiguous table ${definition.title}`);
    if (!matches.length) {
      await api.request('POST', `/api/v2/meta/bases/${base.id}/tables`, {
        title: definition.title, table_name: definition.title,
        columns: definition.columns.filter(column => !column.references).map(columnPayload),
      });
    }
  }
  const tables = await readTables(api, base.id);
  for (const definition of schema.tables) {
    const child = tables.get(definition.title);
    for (const relation of definition.columns.filter(column => column.references)) {
      const parent = tables.get(relation.references);
      const links = child.columns.filter(column => column.colOptions?.type === 'bt'
        && column.colOptions.fk_related_model_id === parent.id);
      if (links.length > 1) throw new Error(`${relation.title}: multiple relations; resolve manually`);
      if (!links.length) {
        await api.request('POST', `/api/v2/meta/tables/${child.id}/columns`, {
          title: relation.title, uidt: relation.uidt, type: 'bt', version: 1,
          parentId: parent.id, childId: child.id,
        });
      }
    }
  }
  return readTables(api, base.id);
}

/**
 * Serialize setup and leave existing bases untouched in start mode.
 * Resume may create missing metadata; provision only verifies existing metadata.
 * SQL changes and completion tracking roll back together; NocoDB API writes do not.
 */
async function initialize(api, database, environment, mode) {
  const title = environment.NOCODB_BASE_NAME || schema.base;
  return database.transaction(async transaction => {
    await transaction.raw('SELECT pg_advisory_xact_lock(hashtext(?))', [`pinkbombs:initialize:${title}`]);
    let base = await findBase(api, title);
    if (base && mode === 'start') return { status: 'existing', base };
    if (!base && mode !== 'start') throw new Error(`Base ${title} is missing; run start.sh first`);
    if (!base) {
      setting(environment, 'API_DB_USER');
      setting(environment, 'API_DB_PASSWORD');
      base = await api.request('POST', '/api/v2/meta/bases/', { title });
    }
    const tables = mode === 'provision' ? await readTables(api, base.id) : await createTables(api, base);
    verifyTables(tables);
    await checkRecords(api, tables);
    await provisionSchema(transaction, tables);
    await provisionApiDatabase(transaction, tables, environment);
    const shared = await api.request('GET', `/api/v2/meta/bases/${base.id}`);
    if (shared.uuid) throw new Error('Disable public base sharing before completing initialization');
    for (const table of tables.values()) {
      const views = await api.list(`/api/v2/meta/tables/${table.id}/views`);
      if (views.some(view => view.uuid)) throw new Error('Disable public view sharing before completing initialization');
    }
    await transaction.raw('CREATE TABLE IF NOT EXISTS pinkbombs_api.installation (base_id text PRIMARY KEY, completed_at timestamptz NOT NULL DEFAULT now())');
    await transaction.raw('INSERT INTO pinkbombs_api.installation (base_id) VALUES (?) ON CONFLICT (base_id) DO NOTHING', [base.id]);
    return { status: 'initialized', base };
  });
}

/**
 * Run start, resume, or provision and return { status, base }.
 * Close only the SQL pool created here; injected dependencies remain caller-owned.
 */
export async function bootstrap(environment = process.env, dependencies = {}) {
  const mode = dependencies.mode || process.argv[2] || 'start';
  if (!['start', 'resume', 'provision'].includes(mode)) throw new Error('Usage: bootstrap.mjs [start|resume|provision]');
  const api = dependencies.api || new NocoApi(environment.NOCODB_API_URL || 'http://nocodb:8080');
  await authenticate(api, environment, mode === 'start');
  const database = dependencies.database || connectDatabase(environment);
  try {
    return await initialize(api, database, environment, mode);
  } finally {
    if (!dependencies.database) await database.destroy();
  }
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  bootstrap().then(result => {
    console.log(result.status === 'existing'
      ? 'Existing NocoDB base left unchanged. Run check.sh to diagnose it; maintenance is explicit.'
      : 'NocoDB base created and verified; submission database provisioned.');
  }).catch(error => {
    console.error(`Initialization failed: ${error.message}. NocoDB remains available. See logs and check.sh; use resume only after review.`);
    process.exitCode = 1;
  });
}import { readFile } from 'node:fs/promises';
