import { readFile } from 'node:fs/promises';
import { createRequire } from 'node:module';
import { pathToFileURL } from 'node:url';

export const schema = JSON.parse(await readFile(new URL('./schema.json', import.meta.url), 'utf8'));

export function columnPayload(column) {
  const payload = { title: column.title, column_name: column.title, uidt: column.uidt };
  if (column.generated) return { ...payload, dt: 'int8', pk: true, ai: true, rqd: true };
  if (column.required) payload.rqd = true;
  if (column.options) {
    payload.colOptions = {
      options: schema.options[column.options].map(({ label }, index) => ({ title: label, order: index + 1 })),
    };
  }
  if (column.uidt === 'Decimal') Object.assign(payload, { dt: 'numeric', dtxp: '30', dtxs: '10' });
  if (column.uidt === 'CreatedTime') payload.meta = { date_format: 'YYYY-MM-DD', time_format: 'HH:mm', timezone: 'UTC' };
  return payload;
}

export function verifyColumn(column, expected) {
  if (expected.generated) {
    if (!column.pk || !column.ai) throw new Error(`${expected.title}: generated primary key required`);
    return;
  }
  if (expected.references) {
    if (!['Links', 'LinkToAnotherRecord'].includes(column.uidt) || column.colOptions?.type !== 'bt') {
      throw new Error(`${expected.title}: belongs-to relation required`);
    }
    return;
  }
  if (column.uidt !== expected.uidt) throw new Error(`${expected.title}: incompatible type ${column.uidt}`);
  if (expected.options) {
    const actual = (column.colOptions?.options || []).map(option => option.title);
    const desired = schema.options[expected.options].map(option => option.label);
    if (JSON.stringify(actual) !== JSON.stringify(desired)) throw new Error(`${expected.title}: incompatible select options`);
  }
  if (expected.title === 'email' && column.unique) {
    throw new Error(`${expected.title}: uniqueness is forbidden`);
  }
}

export function optionConstraintIsCurrent(definition, columnName, labels) {
  if (!definition?.includes(`${columnName} IS NULL`)) return false;
  const existingLabels = [...definition.matchAll(/'((?:''|[^'])*)'/g)]
    .map(([, label]) => label.replaceAll("''", "'"));
  return JSON.stringify(existingLabels) === JSON.stringify(labels);
}

export async function syncColumnOptions(api, tableId, column, expected) {
  const actual = (column.colOptions?.options || []).map(option => option.title);
  const desired = schema.options[expected.options].map(option => option.label);
  if (JSON.stringify(actual) === JSON.stringify(desired)) return column;

  await api.request('PATCH', `/api/v2/meta/columns/${column.id}`, {
    colOptions: columnPayload(expected).colOptions,
  });
  const metadata = await api.request('GET', `/api/v2/meta/tables/${tableId}`);
  const updated = metadata.columns.find(candidate => candidate.id === column.id);
  if (!updated) throw new Error(`${expected.title}: column missing after option update`);
  return updated;
}

export class NocoApi {
  constructor(url, fetcher = fetch) {
    this.url = url.replace(/\/$/, '');
    this.fetcher = fetcher;
    this.token = undefined;
  }

  async request(method, path, body) {
    const response = await this.fetcher(`${this.url}${path}`, {
      method,
      headers: { 'Content-Type': 'application/json', ...(this.token ? { 'xc-auth': this.token } : {}) },
      body: body === undefined ? undefined : JSON.stringify(body),
      signal: AbortSignal.timeout(30000),
    });
    if (!response.ok) throw new Error(`${method} ${path}: HTTP ${response.status}`);
    return response.status === 204 ? {} : response.json();
  }

  async list(path) {
    const records = [];
    let offset = 0;
    for (;;) {
      const response = await this.request('GET', `${path}${path.includes('?') ? '&' : '?'}limit=100&offset=${offset}`);
      const page = response.users || response;
      const entries = Array.isArray(page) ? page : page.list;
      if (!Array.isArray(entries)) throw new Error(`${path}: unexpected list response`);
      records.push(...entries);
      if (Array.isArray(page) || page.pageInfo?.isLastPage !== false) return records;
      if (!entries.length) throw new Error(`${path}: empty pagination page`);
      offset += entries.length;
    }
  }

  async login(email, password, firstUser = false) {
    const result = await this.request('POST', `/api/v2/auth/user/${firstUser ? 'signup' : 'signin'}`, { email, password });
    if (!result.token) throw new Error('Authentication did not return a session token');
    this.token = result.token;
  }
}

function requireSetting(environment, name) {
  if (!environment[name]) throw new Error(`Set ${name} in the private nocodb/.env before initialization`);
  return environment[name];
}

async function ensureTables(api, baseId) {
  const tables = new Map();
  const existing = await api.list(`/api/v2/meta/bases/${baseId}/tables`);
  for (const definition of schema.tables) {
    const matches = existing.filter(table => table.title === definition.title);
    if (matches.length > 1) throw new Error(`Ambiguous table ${definition.title}`);
    const table = matches[0] || await api.request('POST', `/api/v2/meta/bases/${baseId}/tables`, {
      title: definition.title,
      table_name: definition.title,
      columns: definition.columns.filter(column => !column.references).map(columnPayload),
    });
    let metadata = await api.request('GET', `/api/v2/meta/tables/${table.id}`);
    for (const expected of definition.columns.filter(column => !column.references)) {
      let column = metadata.columns.find(candidate => candidate.title === expected.title);
      if (!column && expected.generated) column = metadata.columns.find(candidate => candidate.pk);
      if (!column) {
        await api.request('POST', `/api/v2/meta/tables/${table.id}/columns`, columnPayload(expected));
        metadata = await api.request('GET', `/api/v2/meta/tables/${table.id}`);
        column = metadata.columns.find(candidate => candidate.title === expected.title);
      }
      if (!column) throw new Error(`${definition.title}.${expected.title}: column not returned by API`);
      if (expected.options) column = await syncColumnOptions(api, table.id, column, expected);
      verifyColumn(column, expected);
      if (expected.generated && column.column_name !== 'id') throw new Error(`${definition.title}: physical primary key must be named id`);
    }
    tables.set(definition.title, metadata);
  }
  const parent = tables.get('reponses_pinkometre');
  let child = tables.get('consommations');
  const relation = schema.tables[1].columns.find(column => column.references);
  const existingLinks = child.columns.filter(column => column.colOptions?.type === 'bt' && column.colOptions.fk_related_model_id === parent.id);
  if (existingLinks.length > 1) throw new Error('Multiple response relations; resolve the ambiguity before initialization');
  if (!existingLinks.length) {
    await api.request('POST', `/api/v2/meta/tables/${child.id}/columns`, {
      title: relation.title, uidt: 'Links', type: 'bt', version: 1,
      parentId: parent.id, childId: child.id, meta: { required: true },
    });
  }
  child = await api.request('GET', `/api/v2/meta/tables/${child.id}`);
  let link = child.columns.find(column => column.colOptions?.type === 'bt' && column.colOptions.fk_related_model_id === parent.id);
  if (link && link.title !== relation.title) await api.request('PATCH', `/api/v2/meta/columns/${link.id}`, { title: relation.title });
  child = await api.request('GET', `/api/v2/meta/tables/${child.id}`);
  link = child.columns.find(column => column.colOptions?.type === 'bt' && column.colOptions.fk_related_model_id === parent.id);
  verifyColumn(link || {}, relation);
  if (link.colOptions.fk_related_model_id !== parent.id) throw new Error('Response relation targets the wrong table');
  const foreignKeyColumn = child.columns.find(column => column.id === link.colOptions.fk_child_column_id);
  if (!foreignKeyColumn) throw new Error('Response relation has no physical foreign-key column');
  if (foreignKeyColumn.title !== relation.physicalName) {
    await api.request('PATCH', `/api/v2/meta/columns/${foreignKeyColumn.id}`, { title: relation.physicalName });
  }
  child = await api.request('GET', `/api/v2/meta/tables/${child.id}`);
  tables.set('consommations', child);
  tables.set('reponses_pinkometre', await api.request('GET', `/api/v2/meta/tables/${parent.id}`));
  return tables;
}

function physicalColumn(table, expected) {
  let column = table.columns.find(candidate => candidate.title === expected.title);
  if (expected.generated) column = table.columns.find(candidate => candidate.pk);
  if (expected.references) column = table.columns.find(candidate => candidate.id === column?.colOptions?.fk_child_column_id);
  if (expected.uidt === 'CreatedTime') {
    column = table.columns.find(candidate => candidate.uidt === 'CreatedTime' && candidate.system && candidate.column_name);
  }
  if (!column?.column_name) throw new Error(`${table.title}.${expected.title}: physical column unavailable`);
  return column.column_name;
}

export async function migrateSchema(database, tables) {
  await database.transaction(async transaction => {
    await transaction.raw("SELECT pg_advisory_xact_lock(hashtext('pinkbombs-pinkometre-schema'))");
    const physical = new Map();
    for (const definition of schema.tables) {
      const table = tables.get(definition.title);
      const result = await transaction.raw(
        "SELECT table_schema FROM information_schema.tables WHERE table_name = ? AND table_schema = ?",
        [table.table_name, table.base_id],
      );
      if (result.rows.length !== 1) throw new Error(`${definition.title}: physical table is missing or ambiguous`);
      const qualified = `${result.rows[0].table_schema}.${table.table_name}`;
      const columns = new Map(definition.columns.map(column => [column.title, column.physicalName || physicalColumn(table, column)]));
      physical.set(definition.title, { qualified, columns });
      for (const column of definition.columns.filter(candidate => candidate.references && candidate.physicalName)) {
        const currentName = physicalColumn(table, column);
        const targetName = column.physicalName;
        if (currentName === targetName) continue;
        const existingColumns = await transaction.raw(
          'SELECT column_name FROM information_schema.columns WHERE table_schema = ? AND table_name = ? AND column_name IN (?, ?)',
          [result.rows[0].table_schema, table.table_name, currentName, targetName],
        );
        const names = new Set(existingColumns.rows.map(row => row.column_name));
        if (names.has(currentName) && names.has(targetName)) throw new Error(`${definition.title}: both legacy and target foreign-key columns exist`);
        if (names.has(currentName)) {
          await transaction.raw('ALTER TABLE ?? RENAME COLUMN ?? TO ??', [qualified, currentName, targetName]);
        } else if (!names.has(targetName)) {
          throw new Error(`${definition.title}: physical foreign-key column is missing`);
        }
      }
      if (definition.title === 'reponses_pinkometre') {
        const legacyFingerprint = table.columns.find(column => column.title === 'empreinte_ip_hmac');
        if (legacyFingerprint?.column_name) {
          await transaction.raw('ALTER TABLE ?? DROP COLUMN IF EXISTS ??', [qualified, legacyFingerprint.column_name]);
        }
        const legacyCreatedTime = table.columns.find(column => column.title === 'date_creation_utc');
        if (legacyCreatedTime?.column_name) {
          await transaction.raw('ALTER TABLE ?? DROP COLUMN IF EXISTS ??', [qualified, legacyCreatedTime.column_name]);
        }
      }
      if (definition.title === 'consommations') {
        const legacyIndex = `pb_${table.id}_reponses_pinkometre_id`.slice(0, 63);
        await transaction.raw('DROP INDEX IF EXISTS ??.??', [result.rows[0].table_schema, legacyIndex]);
      }
      for (const column of definition.columns) {
        if (column.generated) continue;
        const name = columns.get(column.title);
        if (column.uidt === 'Decimal') await transaction.raw('ALTER TABLE ?? ALTER COLUMN ?? TYPE numeric', [qualified, name]);
        if (column.uidt === 'CreatedTime') {
          await transaction.raw('ALTER TABLE ?? ALTER COLUMN ?? SET DEFAULT CURRENT_TIMESTAMP', [qualified, name]);
        }
        if (column.required) await transaction.raw('ALTER TABLE ?? ALTER COLUMN ?? SET NOT NULL', [qualified, name]);
        if (column.options) {
          const constraint = `pb_${table.id}_${column.title}_options`;
          const allowed = schema.options[column.options].map(option => option.label);
          const existing = await transaction.raw('SELECT 1 FROM pg_constraint WHERE conrelid = ?::regclass AND conname = ?', [qualified, constraint]);
          const currentDefinition = existing.rows.length
            ? await transaction.raw('SELECT pg_get_constraintdef(oid) AS definition FROM pg_constraint WHERE conrelid = ?::regclass AND conname = ?', [qualified, constraint])
            : null;
          const isCurrent = currentDefinition?.rows[0]
            ? optionConstraintIsCurrent(currentDefinition.rows[0].definition, name, allowed)
            : false;
          if (!isCurrent && existing.rows.length) {
            await transaction.raw('ALTER TABLE ?? DROP CONSTRAINT ??', [qualified, constraint]);
          }
          if (!isCurrent) {
            const literals = allowed.map(label => `'${label.replaceAll("'", "''")}'`).join(', ');
            await transaction.raw(`ALTER TABLE ?? ADD CONSTRAINT ?? CHECK (?? IS NULL OR ?? IN (${literals}))`, [qualified, constraint, name, name]);
          }
        }
      }
      for (const columns of definition.indexes) {
        const index = `pb_${table.id}_${columns.join('_')}`.slice(0, 63);
        const bindings = [index, qualified, ...columns.map(name => physical.get(definition.title).columns.get(name))];
        await transaction.raw(`CREATE INDEX IF NOT EXISTS ?? ON ?? (${columns.map(() => '??').join(', ')})`, bindings);
        const verified = await transaction.raw(
          'SELECT index.indisvalid, index.indisunique, array_agg(attribute.attname::text ORDER BY key.ordinality) AS columns FROM pg_index index JOIN pg_class index_table ON index_table.oid = index.indexrelid CROSS JOIN LATERAL unnest(index.indkey) WITH ORDINALITY AS key(attnum, ordinality) JOIN pg_attribute attribute ON attribute.attrelid = index.indrelid AND attribute.attnum = key.attnum WHERE index.indrelid = ?::regclass AND index_table.relname = ? GROUP BY index.indisvalid, index.indisunique',
          [qualified, index],
        );
        if (!verified.rows[0]?.indisvalid || verified.rows[0].indisunique || JSON.stringify(verified.rows[0].columns) !== JSON.stringify(columns.map(name => physical.get(definition.title).columns.get(name)))) {
          throw new Error(`${definition.title}: incompatible index ${index}`);
        }
      }
      for (const column of definition.columns.filter(column => column.title === 'email')) {
        const unique = await transaction.raw(
          'SELECT 1 FROM pg_index index JOIN pg_attribute attribute ON attribute.attrelid = index.indrelid AND attribute.attnum = ANY(index.indkey) WHERE index.indrelid = ?::regclass AND index.indisunique AND attribute.attname = ?',
          [qualified, columns.get(column.title)],
        );
        if (unique.rows.length) throw new Error(`${column.title}: existing unique index is forbidden`);
      }
    }
    const child = physical.get('consommations');
    const parent = physical.get('reponses_pinkometre');
    const foreignKey = child.columns.get('reponse_pinkometre');
    const constraints = await transaction.raw(
      "SELECT 1 FROM pg_constraint constraint_record JOIN pg_attribute attribute ON attribute.attrelid = constraint_record.conrelid AND attribute.attnum = ANY(constraint_record.conkey) WHERE constraint_record.contype = 'f' AND constraint_record.conrelid = ?::regclass AND constraint_record.confrelid = ?::regclass AND attribute.attname = ?",
      [child.qualified, parent.qualified, foreignKey],
    );
    if (!constraints.rows.length) {
      await transaction.raw('ALTER TABLE ?? ADD CONSTRAINT ?? FOREIGN KEY (??) REFERENCES ?? (??) ON DELETE NO ACTION ON UPDATE NO ACTION',
        [child.qualified, `pb_${tables.get('consommations').id}_response_fk`, foreignKey, parent.qualified, parent.columns.get('id')]);
    }
  });
}

async function restrictAccess(api, baseId, tables, environment) {
  const adminEmail = environment.NOCODB_BOOTSTRAP_EMAIL;
  const members = await api.list(`/api/v2/meta/bases/${baseId}/users`);
  for (const member of members) {
    if (member.email?.toLowerCase() === adminEmail.toLowerCase()) continue;
    const current = typeof member.roles === 'string' ? member.roles : Object.keys(member.roles || {}).filter(key => member.roles[key]).join(',');
    if (current !== 'viewer') {
      await api.request('PATCH', `/api/v2/meta/bases/${baseId}/users/${member.fk_user_id || member.id}`, { roles: 'viewer' });
    }
  }
  await api.request('PATCH', `/api/v2/meta/bases/${baseId}`, { uuid: null });
  for (const table of tables.values()) {
    for (const view of await api.list(`/api/v2/meta/tables/${table.id}/views`)) {
      if (view.uuid) await api.request('DELETE', `/api/v2/meta/views/${view.id}/share`);
    }
  }
  const verified = await api.list(`/api/v2/meta/bases/${baseId}/users`);
  for (const member of verified) {
    if (member.email?.toLowerCase() === adminEmail.toLowerCase()) continue;
    const roles = typeof member.roles === 'string' ? member.roles : Object.keys(member.roles || {}).filter(key => member.roles[key]).join(',');
    if (roles !== 'viewer') throw new Error('Base viewer permission verification failed');
  }
  const base = await api.request('GET', `/api/v2/meta/bases/${baseId}`);
  if (base.uuid) throw new Error('Public base sharing remains enabled');
  for (const table of tables.values()) {
    const views = await api.list(`/api/v2/meta/tables/${table.id}/views`);
    if (views.some(view => view.uuid)) throw new Error(`${table.title}: public view sharing remains enabled`);
  }
}

export const apiInsertColumns = {
  reponses_pinkometre: ['email', 'impact_initial', 'impact_apres_engagement', 'alternative_choisie', 'supplement_choisi', 'consentement_omega3'],
  consommations: ['reponse_pinkometre', 'scenario', 'produit', 'variante', 'frequence', 'occurence_par_an', 'quantite_par_occurrence', 'unite_fr', 'poids_annuel_kg'],
};

async function syncRelationColumnName(api, tables) {
  const table = tables.get('consommations');
  const relation = schema.tables.find(definition => definition.title === 'consommations').columns.find(column => column.references);
  const link = table.columns.find(column => column.title === relation.title);
  const physicalColumnMetadata = table.columns.find(column => column.id === link?.colOptions?.fk_child_column_id);
  if (!physicalColumnMetadata) throw new Error('Response relation has no physical foreign-key column');
  if (physicalColumnMetadata.column_name !== relation.physicalName) {
    await api.request('PATCH', `/api/v2/meta/columns/${physicalColumnMetadata.id}`, { column_name: relation.physicalName });
  }
  const refreshed = await api.request('GET', `/api/v2/meta/tables/${table.id}`);
  const updated = refreshed.columns.find(column => column.id === physicalColumnMetadata.id);
  if (updated?.column_name !== relation.physicalName) throw new Error('Physical foreign-key column name did not update');
  tables.set('consommations', refreshed);
}

async function setViewColumnVisibility(api, view, viewColumns, column, visible) {
  let viewColumn = viewColumns.find(candidate => candidate.fk_column_id === column.id);
  if (viewColumn) {
    if (viewColumn.show !== visible) {
      await api.request('PATCH', `/api/v2/meta/views/${view.id}/columns/${viewColumn.id}`, { show: visible });
    }
    return;
  }
  if (!visible) return;
  const order = Math.max(0, ...viewColumns.map(candidate => Number(candidate.order) || 0)) + 1;
  await api.request('POST', `/api/v2/meta/views/${view.id}/columns`, {
    fk_column_id: column.id,
    show: true,
    order,
  });
}

export async function configureDefaultViews(api, tables) {
  for (const tableName of ['reponses_pinkometre', 'consommations']) {
    const table = tables.get(tableName);
    const metadata = await api.request('GET', `/api/v2/meta/tables/${table.id}`);
    const views = await api.list(`/api/v2/meta/tables/${table.id}/views`);
    const view = views.find(candidate => candidate.type === 3 && candidate.show)
      || views.find(candidate => candidate.type === 3);
    if (!view) throw new Error(`${tableName}: default grid view is unavailable`);
    const viewColumns = await api.list(`/api/v2/meta/views/${view.id}/columns`);
    if (tableName === 'consommations') {
      const relation = schema.tables.find(definition => definition.title === tableName).columns.find(column => column.references);
      const link = metadata.columns.find(column => column.title === relation.title);
      const foreignKeyColumn = metadata.columns.find(column => column.id === link?.colOptions?.fk_child_column_id);
      if (!link || !foreignKeyColumn || foreignKeyColumn.column_name !== relation.physicalName) {
        throw new Error(`${tableName}: renamed response foreign-key metadata is unavailable`);
      }
      await setViewColumnVisibility(api, view, viewColumns, link, false);
      await setViewColumnVisibility(api, view, viewColumns, foreignKeyColumn, true);
    } else {
      const createdAt = metadata.columns.find(column => column.uidt === 'CreatedTime' && column.system && column.column_name === 'created_at');
      if (!createdAt) throw new Error(`${tableName}: system CreatedAt field is unavailable`);
      await setViewColumnVisibility(api, view, viewColumns, createdAt, true);
    }
    const verified = await api.list(`/api/v2/meta/views/${view.id}/columns`);
    if (tableName === 'consommations') {
      const relation = schema.tables.find(definition => definition.title === tableName).columns.find(column => column.references);
      const link = metadata.columns.find(column => column.title === relation.title);
      const foreignKeyColumn = metadata.columns.find(column => column.id === link.colOptions.fk_child_column_id);
      if (verified.find(column => column.fk_column_id === link.id)?.show !== false
        || verified.find(column => column.fk_column_id === foreignKeyColumn.id)?.show !== true) {
        throw new Error(`${tableName}: grid must show the scalar foreign key instead of the response relation`);
      }
    } else {
      const createdAt = metadata.columns.find(column => column.uidt === 'CreatedTime' && column.system && column.column_name === 'created_at');
      if (verified.find(column => column.fk_column_id === createdAt.id)?.show !== true) {
        throw new Error(`${tableName}: system CreatedAt must be visible in the grid`);
      }
    }
  }
}

class ApiRoleAccessError extends Error {}

async function checkApiRole(transaction, username) {
  const result = await transaction.raw(`
    SELECT role.rolsuper, role.rolcreatedb, role.rolcreaterole, role.rolreplication,
      role.rolbypassrls,
      EXISTS (SELECT 1 FROM pg_auth_members WHERE member = role.oid) AS memberships,
      EXISTS (SELECT 1 FROM pg_shdepend WHERE refclassid = 'pg_authid'::regclass
        AND refobjid = role.oid AND deptype = 'o'
        AND (dbid = 0 OR dbid = (SELECT oid FROM pg_database WHERE datname = current_database()))) AS ownership
    FROM pg_roles role WHERE rolname = ?`, [username]);
  const role = result.rows[0];
  if (role && Object.values(role).some(Boolean)) {
    throw new ApiRoleAccessError('API_DB_USER has administrative attributes, role memberships, or ownership; use a dedicated unprivileged role');
  }
  return role;
}

async function verifyApiPrivileges(transaction, username, kind, object, allowed, column) {
  const privileges = {
    table: ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'TRUNCATE', 'REFERENCES', 'TRIGGER', 'MAINTAIN'],
    column: ['SELECT', 'INSERT', 'UPDATE', 'REFERENCES'],
    schema: ['USAGE', 'CREATE'],
    sequence: ['USAGE', 'SELECT', 'UPDATE'],
  }[kind];
  const argumentsSql = kind === 'column' ? '?::name, ?::oid, ?::text, privilege' : '?::name, ?::oid, privilege';
  const bindings = kind === 'column' ? [username, object, column, username, object, column] : [username, object, username, object];
  const result = await transaction.raw(`
    SELECT privilege, has_${kind}_privilege(${argumentsSql}) AS access,
      has_${kind}_privilege(${argumentsSql} || ' WITH GRANT OPTION') AS grantable
    FROM unnest(?::text[]) AS privileges(privilege)`, [...bindings, privileges]);
  for (const permission of result.rows) {
    if (permission.access !== allowed.includes(permission.privilege) || permission.grantable) {
      throw new ApiRoleAccessError(`API_DB_USER has incompatible effective ${kind} privileges (${permission.privilege}); check PUBLIC grants or use a dedicated role`);
    }
  }
}

async function resetApiTablePrivileges(transaction, username, schemaName, tableName) {
  const result = await transaction.raw(`
    SELECT relation.oid, attribute.attname
    FROM pg_class relation JOIN pg_namespace namespace ON namespace.oid = relation.relnamespace
    JOIN pg_attribute attribute ON attribute.attrelid = relation.oid
    WHERE namespace.nspname = ? AND relation.relname = ?
      AND attribute.attnum > 0 AND NOT attribute.attisdropped
    ORDER BY attribute.attnum`, [schemaName, tableName]);
  if (!result.rows.length) throw new ApiRoleAccessError('API database table is unavailable');
  await transaction.raw('REVOKE ALL PRIVILEGES ON TABLE ??.?? FROM ?? RESTRICT', [schemaName, tableName, username]);
  const columns = result.rows.map(row => row.attname);
  const placeholders = columns.map(() => '??').join(', ');
  await transaction.raw(
    `REVOKE SELECT (${placeholders}), INSERT (${placeholders}), UPDATE (${placeholders}), REFERENCES (${placeholders}) ON TABLE ??.?? FROM ?? RESTRICT`,
    [...columns, ...columns, ...columns, ...columns, schemaName, tableName, username],
  );
  return { oid: result.rows[0].oid, columns };
}

export async function provisionApiDatabase(database, tables, environment) {
  const username = requireSetting(environment, 'API_DB_USER');
  const password = requireSetting(environment, 'API_DB_PASSWORD');
  if (!/^[a-zA-Z_][a-zA-Z0-9_]{0,62}$/.test(username) || username === 'pinkbombs') {
    throw new Error('API_DB_USER must be a separate, valid PostgreSQL role name');
  }

  const baseSchema = tables.get('reponses_pinkometre')?.base_id;
  if (!baseSchema || !/^[a-zA-Z0-9_]+$/.test(baseSchema)) throw new Error('NocoDB base schema is unavailable');
  const responseTable = tables.get('reponses_pinkometre');
  const consumptionTable = tables.get('consommations');
  if (!responseTable || !consumptionTable) throw new Error('Pinkometre tables are unavailable');

  await database.transaction(async transaction => {
    await transaction.raw('SELECT pg_advisory_xact_lock(hashtext(?))', [`pinkbombs-api-role:${username}`]);
    const role = await checkApiRole(transaction, username);
    const roleStatement = await transaction.raw(
      'SELECT format(?::text, ?::text, ?::text) AS statement',
      [`${role ? 'ALTER' : 'CREATE'} ROLE %I WITH LOGIN PASSWORD %L NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOREPLICATION NOBYPASSRLS`, username, password],
    );
    await transaction.raw(roleStatement.rows[0].statement);
    await transaction.raw('CREATE SCHEMA IF NOT EXISTS ?? AUTHORIZATION pinkbombs', ['pinkbombs_api']);
    await transaction.raw('CREATE TABLE IF NOT EXISTS ??.?? (key_hash varchar(64) PRIMARY KEY, request_hash varchar(64) NOT NULL, response_id integer NOT NULL, created_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP)', ['pinkbombs_api', 'idempotency_keys']);
    for (const schemaName of [baseSchema, 'pinkbombs_api']) {
      const namespace = await transaction.raw('SELECT oid FROM pg_namespace WHERE nspname = ?', [schemaName]);
      if (!namespace.rows[0]) throw new ApiRoleAccessError('API database schema is unavailable');
      await transaction.raw('REVOKE ALL PRIVILEGES ON SCHEMA ?? FROM ?? RESTRICT', [schemaName, username]);
      await transaction.raw('GRANT USAGE ON SCHEMA ?? TO ??', [schemaName, username]);
      await verifyApiPrivileges(transaction, username, 'schema', namespace.rows[0].oid, ['USAGE']);
    }
    const idempotency = await resetApiTablePrivileges(transaction, username, 'pinkbombs_api', 'idempotency_keys');
    await transaction.raw('GRANT SELECT, INSERT, DELETE ON TABLE ??.?? TO ??', ['pinkbombs_api', 'idempotency_keys', username]);
    await verifyApiPrivileges(transaction, username, 'table', idempotency.oid, ['SELECT', 'INSERT', 'DELETE']);
    for (const column of idempotency.columns) {
      await verifyApiPrivileges(transaction, username, 'column', idempotency.oid, ['SELECT', 'INSERT'], column);
    }

    for (const [title, fieldNames] of Object.entries(apiInsertColumns)) {
      const table = tables.get(title);
      const physical = await resetApiTablePrivileges(transaction, username, baseSchema, table.table_name);
      const columns = fieldNames.map(name => {
        const expected = schema.tables.find(definition => definition.title === title).columns.find(column => column.title === name);
        if (!expected) throw new Error(`${title}.${name}: API column is not declared in schema`);
        return physicalColumn(table, expected);
      });
      await transaction.raw(
        `GRANT INSERT (${columns.map(() => '??').join(', ')}) ON TABLE ??.?? TO ??`,
        [...columns, baseSchema, table.table_name, username],
      );
      const idColumn = physicalColumn(
        table,
        schema.tables.find(definition => definition.title === title).columns.find(column => column.title === 'id'),
      );
      await transaction.raw('GRANT SELECT (??) ON TABLE ??.?? TO ??', [idColumn, baseSchema, table.table_name, username]);
      const sequence = await transaction.raw(`
        SELECT sequence.oid, namespace.nspname AS schema, sequence.relname AS name
        FROM pg_class sequence JOIN pg_namespace namespace ON namespace.oid = sequence.relnamespace
        WHERE sequence.oid = pg_get_serial_sequence(format('%I.%I', ?::text, ?::text), ?)::regclass`,
      [baseSchema, table.table_name, idColumn]);
      if (!sequence.rows[0]) throw new ApiRoleAccessError(`${title}: generated ID sequence is unavailable`);
      const { schema: sequenceSchema, name: sequenceName, oid: sequenceOid } = sequence.rows[0];
      await transaction.raw('REVOKE ALL PRIVILEGES ON SEQUENCE ??.?? FROM ?? RESTRICT', [sequenceSchema, sequenceName, username]);
      await transaction.raw('GRANT USAGE ON SEQUENCE ??.?? TO ??', [sequenceSchema, sequenceName, username]);
      await verifyApiPrivileges(transaction, username, 'sequence', sequenceOid, ['USAGE']);
      await verifyApiPrivileges(transaction, username, 'table', physical.oid, []);
      for (const column of physical.columns) {
        const allowed = [];
        if (columns.includes(column)) allowed.push('INSERT');
        if (column === idColumn) allowed.push('SELECT');
        await verifyApiPrivileges(transaction, username, 'column', physical.oid, allowed, column);
      }
    }
    await checkApiRole(transaction, username);
    await transaction.raw('ALTER ROLE ?? SET search_path TO ??, ??', [username, baseSchema, 'pinkbombs_api']);
  }).catch(error => {
    if (error instanceof ApiRoleAccessError) throw error;
    throw new Error('API database role provisioning failed and was rolled back; check dependent grants and use a dedicated unprivileged API_DB_USER');
  });
}

export async function bootstrap(environment = process.env) {
  const email = requireSetting(environment, 'NOCODB_BOOTSTRAP_EMAIL');
  const password = requireSetting(environment, 'NOCODB_BOOTSTRAP_PASSWORD');
  requireSetting(environment, 'API_DB_USER');
  requireSetting(environment, 'API_DB_PASSWORD');
  const api = new NocoApi(environment.NOCODB_API_URL || 'http://nocodb:8080');
  const info = await api.request('GET', '/api/v1/db/meta/nocodb/info');
  await api.login(email, password, info.firstUser === true);
  const baseTitle = environment.NOCODB_BASE_NAME || schema.base;
  const bases = (await api.list('/api/v2/meta/bases/')).filter(base => base.title === baseTitle);
  if (bases.length > 1) throw new Error('Multiple pinkbombs bases; resolve the ambiguity before initialization');
  const base = bases[0] || await api.request('POST', '/api/v2/meta/bases/', { title: baseTitle });
  const tables = await ensureTables(api, base.id);
  const responseTable = tables.get('reponses_pinkometre');
  const legacyFingerprint = responseTable.columns.find(column => column.title === 'empreinte_ip_hmac');
  if (legacyFingerprint) {
    if (!legacyFingerprint.column_name) throw new Error('Legacy IP fingerprint physical column is unavailable');
    await api.request('DELETE', `/api/v2/meta/columns/${legacyFingerprint.id}`);
  }
  const legacyCreatedTime = responseTable.columns.find(column => column.title === 'date_creation_utc');
  if (legacyCreatedTime) await api.request('DELETE', `/api/v2/meta/columns/${legacyCreatedTime.id}`);
  const runtimeRequire = createRequire('/usr/src/app/package.json');
  const database = runtimeRequire('knex')({
    client: 'pg', connection: { host: 'db', port: 5432, user: 'pinkbombs', database: 'pinkbombs', password: requireSetting(environment, 'POSTGRES_PASSWORD') },
    pool: { min: 0, max: 1 },
  });
  try {
    await migrateSchema(database, tables);
    await syncRelationColumnName(api, tables);
    await configureDefaultViews(api, tables);
    await provisionApiDatabase(database, tables, environment);
  } finally {
    await database.destroy();
  }
  await restrictAccess(api, base.id, tables, environment);
  console.log('Pinkometre schema initialized; API database role provisioned; NocoDB members restricted to viewers.');
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  bootstrap().catch(error => {
    console.error(`Initialization failed: ${error.message}`);
    process.exitCode = 1;
  });
}