import assert from 'node:assert/strict';

const environment = process.env;
const baseTitle = environment.NOCODB_BASE_NAME || 'pinkbombs';
const admin = new NocoApi(environment.NOCODB_API_URL || 'http://nocodb:8080');

await admin.login(environment.NOCODB_BOOTSTRAP_EMAIL, environment.NOCODB_BOOTSTRAP_PASSWORD);
const base = (await admin.list('/api/v2/meta/bases/')).find(candidate => candidate.title === baseTitle);
assert.ok(base, `Base ${baseTitle} is unavailable`);

const [tables, members] = await Promise.all([
  admin.list(`/api/v2/meta/bases/${base.id}/tables`),
  admin.list(`/api/v2/meta/bases/${base.id}/users`),
]);
for (const title of ['reponses_pinkometre', 'consommations']) {
  const table = tables.find(candidate => candidate.title === title);
  assert.ok(table, `Missing table ${title}`);
  const records = await admin.request('GET', `/api/v2/tables/${table.id}/records?limit=1`);
  assert.ok(Array.isArray(records.list), `${title}: NocoDB records are not readable`);
}

for (const member of members) {
  if (member.email?.toLowerCase() === environment.NOCODB_BOOTSTRAP_EMAIL.toLowerCase()) continue;
  const roles = typeof member.roles === 'string'
    ? member.roles
    : Object.keys(member.roles || {}).filter(role => member.roles[role]).join(',');
  assert.equal(roles, 'viewer', `${member.email}: NocoDB viewers must not have write access`);
}

console.log('PASS: NocoDB reads both submission tables; all non-admin base members are viewers.');
