import { readFile } from 'node:fs/promises';

export const schema = JSON.parse(await readFile(new URL('schema.json', import.meta.url), 'utf8'));

/** Read a required setting, reporting only its name when missing. */
export function setting(environment, name) {
  const value = environment[name];
  if (!value) throw new Error(`Missing ${name}; configure nocodb/.env before initialization`);
  return value;
}

/** NocoDB HTTP client with session authentication, bounded requests, and paginated reads. */
export class NocoApi {
  constructor(url, fetcher = globalThis.fetch) {
    this.url = url.replace(/\/+$/, '');
    this.fetcher = fetcher;
  }

  /** Send a JSON request; omit response bodies from errors to avoid exposing private data. */
  async request(method, path, value) {
    const headers = { 'Content-Type': 'application/json' };
    if (this.token) headers['xc-auth'] = this.token;
    const result = await this.fetcher(this.url + path, {
      method, headers,
      body: value === undefined ? undefined : JSON.stringify(value),
      signal: AbortSignal.timeout(30000),
    });
    if (!result.ok) throw new Error(`NocoDB ${method} ${path} failed (HTTP ${result.status})`);
    return result.status === 204 ? null : result.json();
  }

  /** Sign in or create the first account, retaining its token for subsequent requests. */
  async login(email, password, signup = false) {
    const session = await this.request('POST', `/api/v2/auth/user/${signup ? 'signup' : 'signin'}`, { email, password });
    if (!session?.token) throw new Error('NocoDB authentication returned no token');
    this.token = session.token;
  }

  /** Collect all list pages, including the users wrapper, without changing metadata. */
  async list(path) {
    const records = [];
    while (true) {
      const separator = path.includes('?') ? '&' : '?';
      const response = await this.request('GET', `${path}${separator}limit=100&offset=${records.length}`);
      const page = response.users ?? response;
      const items = Array.isArray(page) ? page : page.list;
      if (!Array.isArray(items)) throw new Error(`Unexpected NocoDB list at ${path}`);
      records.push(...items);
      if (Array.isArray(page) || page.pageInfo?.isLastPage !== false) return records;
      if (items.length === 0) throw new Error(`Empty NocoDB pagination page at ${path}`);
    }
  }
}

/** Build a column-creation payload using French labels rather than application codes. */
export function columnPayload(definition) {
  const result = { title: definition.title, column_name: definition.title, uidt: definition.uidt };
  if (definition.generated) Object.assign(result, { dt: 'int8', pk: true, ai: true, rqd: true });
  if (definition.required) result.rqd = true;
  if (definition.uidt === 'Decimal') Object.assign(result, { dt: 'numeric', dtxp: '30', dtxs: '10' });
  if (definition.options) {
    result.colOptions = { options: schema.options[definition.options].map((option, position) => ({ title: option.label, order: position + 1 })) };
  }
  return result;
}

/** Resolve a column's SQL name, following relation metadata to its generated foreign key. */
export function physicalColumn(table, definition) {
  const matches = table.columns.filter(column => definition.generated ? column.pk : column.title === definition.title);
  if (matches.length !== 1) throw new Error(`${table.title}.${definition.title}: missing or ambiguous column`);
  let column = matches[0];
  if (definition.references) {
    if (column.colOptions?.type !== 'bt') throw new Error(`${definition.title}: expected belongs-to relation`);
    column = table.columns.find(candidate => candidate.id === column.colOptions.fk_child_column_id);
  }
  if (!column?.column_name) throw new Error(`${definition.title}: physical column is unavailable`);
  return column.column_name;
}

/** Read expected tables into a title-keyed Map; reject missing or ambiguous matches. */
export async function readTables(api, baseId) {
  const available = await api.list(`/api/v2/meta/bases/${baseId}/tables`);
  const tables = new Map();
  for (const definition of schema.tables) {
    const matches = available.filter(table => table.title === definition.title);
    if (matches.length !== 1) throw new Error(`${definition.title}: missing or ambiguous table; run diagnostics`);
    tables.set(definition.title, await api.request('GET', `/api/v2/meta/tables/${matches[0].id}`));
  }
  return tables;
}

/** Reject incompatible columns, relations, or options without repairing existing metadata. */
export function verifyTables(tables) {
  for (const definition of schema.tables) {
    const table = tables.get(definition.title);
    if (table.table_name !== definition.title) throw new Error(`${definition.title}: unexpected physical table name`);
    for (const expected of definition.columns) {
      const name = physicalColumn(table, expected);
      const column = table.columns.find(candidate => candidate.column_name === name);
      if (expected.generated) {
        if (name !== 'id' || !column.ai) throw new Error(`${definition.title}: generated id required`);
      } else if (expected.references) {
        const link = table.columns.find(candidate => candidate.title === expected.title);
        if (link.colOptions.fk_related_model_id !== tables.get(expected.references).id) throw new Error(`${expected.title}: incorrect relation target`);
      } else {
        if (name !== expected.title || column.uidt !== expected.uidt) throw new Error(`${expected.title}: incompatible column`);
        if (expected.options) {
          const actual = column.colOptions?.options?.map(option => option.title);
          const desired = schema.options[expected.options].map(option => option.label);
          if (JSON.stringify(actual) !== JSON.stringify(desired)) throw new Error(`${expected.title}: incompatible select options`);
        }
        if (expected.title === 'email' && column.unique) throw new Error('email must not be unique');
      }
    }
  }
}

/** Read both records and default UI grids to detect broken relations without writing data. */
export async function checkRecords(api, tables) {
  for (const table of tables.values()) {
    const result = await api.request('GET', `/api/v2/tables/${table.id}/records?limit=1`);
    if (!Array.isArray(result.list)) throw new Error(`${table.title}: records are not readable`);
    const views = await api.list(`/api/v2/meta/tables/${table.id}/views`);
    const grid = views.find(view => view.type === 3 && view.show) || views.find(view => view.type === 3);
    if (!grid) throw new Error(`${table.title}: default grid is missing`);
    const rows = await api.request('GET', `/api/v1/db/data/noco/${table.base_id}/${table.id}/views/${grid.id}?limit=1`);
    if (!Array.isArray(rows.list)) throw new Error(`${table.title}: grid rows are not readable`);
  }
}