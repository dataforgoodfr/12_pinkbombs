Pinkbombs
================


This repository contains the data tools behind the [Pinkbombs website](https://www.pinkbombs.org):

- For PinkBombs V2 : data management with NocoDB and PostgreSQL for the Pinkometre.
- For PinkBombs V1 :
  - CSV preparation, translation, and download packaging.
  - Python generation of interactive graphs and maps.



# Contributing

## Use Poetry

[Install Poetry](https://python-poetry.org/docs/):

    python3 -m pip install "poetry==1.4.0"

Install dependencies:

    poetry install

Add a dependency:

    poetry add pandas

Update dependencies:

    poetry update

## Use a venv 

    python3 -m venv name-of-your-venv

    source name-of-your-venv/bin/activate

## Pre-commit Checks

Run these commands from the repository root after installing the development dependencies with `poetry install`. Install Node.js 24 LTS, Bash, and OpenSSL for the NocoDB checks; Docker and a running database are not needed.

```bash
poetry run pre-commit install
poetry run pre-commit run --all-files
```

`install` enables the Git hook for future commits. Normally only staged files determine which checks run; `--all-files` checks the whole repository. If Ruff or Black changes a file, review it, stage it again, and retry the commit.

The existing Ruff and Black hooks format/lint Python code, including `pinkbombs_api/` and its tests. The following checks cover the database setup and API:

| Check | What It Validates |
| --- | --- |
| `check-json` | The syntax of `nocodb/schema.json`. |
| `check-yaml` | The syntax of `nocodb/compose.yaml`; this does not validate Docker deployment or environment values. |
| `nocodb-javascript-syntax` | Every staged NocoDB `.mjs` file parses with Node.js. |
| `nocodb-shell-syntax` | Every staged NocoDB `.sh` script parses with Bash. |
| `nocodb-unit-tests` | Initializer behavior, schema options, metadata mapping, and private environment-file setup using disposable fixtures. |
| `pinkbombs-api-unit-tests` | API validation, option mapping, idempotency, rate limiting, CORS, and response-relation checks using test doubles. |

NocoDB unit tests run when NocoDB files change. API unit tests run when API code, submission tests, the shared schema, or Python project configuration changes. Changing the hook configuration also runs both suites. The API hook installs its own test dependencies in a pre-commit-managed Python environment, without graph dependencies. The first run requires network access to install hook environments; subsequent runs reuse them.

To run just the two unit-test hooks across all files:

```bash
poetry run pre-commit run nocodb-unit-tests --all-files
poetry run pre-commit run pinkbombs-api-unit-tests --all-files
```

These hooks do not start containers, initialize NocoDB, or connect to PostgreSQL/Redis. Real database tests and the live NocoDB diagnostic remain explicit commands in [Tests](#tests). GitHub Actions runs the same pre-commit configuration with Node.js 24.
 
## Test the code with Tox

    tox -vv

## PinkBombs V1 - How to
### Generate the graphs and maps
Activate your virtual environment:

    source name-of-your-venv/bin/activate

Run the generation script:

    python pinkbombs/generate.py

The graphs and maps will be added to the `data` directory. They are separated by type (`graphs`and `maps`) and by language (`fr`and `en`):
    
    data
    ├── graphs
    │   ├── en
    │   └── fr
    └── maps
        ├── en
        └── fr

Copy these to the [Pinkbombs webapp reppository](https://github.com/dataforgoodfr/12_pinkbombs_app) in the `public/dashboard/` directory.

**NOTE**: This is a temporary feature, when the images are moved to S3, a workflow will do this automatically upon merge.

### Adding a new visualization
To add a new graph or map, add a function that generates the visualization in the `pinkbombs/graphs/viz.py` or `pinkbombs/graphs/maps_viz.py` files respectively.

**The function NEEDS to return a Plotly Figure object for graphs or an html string for maps**

Make sure that the function is the import in the  `__init__.py` file in the graphs directory:

    from .viz import my_viz_function
    from .maps_viz import my_map_viz_function

The maps needs to the be added to the `config.py` file in order to have it automatically generated. Add the function to the correct section:

    MAPPING     -->     graphs/en
    MAPPINGFR   -->     graphs/fr
    MAPS        -->     maps/en
    MAPSFR      -->     maps/fr

__Be sure to add to both the french and english section.__

The function needs to be added in the following dictionary entry format:

    "visualisation-id": {
        "filename": "source-data.csv",
        "function": pb.my_viz_function,
        "parser": pd.read_csv, # or pd.read_excel for example
        "arguments": [ # add all the arguments in an ordered list
            "arg1",
            "arg2",
            "arg3",
            True,
            0
        ],
    },

Do not skip any argument to the function as these need to be in the correct order.

### Temporary Python scripts for testing locally
To run the plotly graphs locally and generate html files you can view in your browser, you can use the script:

    python3 pinkbombs/graphs/test_graphs.py 

Note that the changes to the html files in this folder won't be included in git as the folder `pinkbombs/graphs/test_html/` is included in `.gitignore`.  

To translate the data and zip the csv files for download, run locally: 

    python3 pinkbombs/graphs/translate_data.py
    python3 pinkbombs/graphs/zip_data.py

Note that this will regenerate all files and may not be adapted


## PinkBombs V2 - NocoDB Data Management


First startup creates the Pinkometre base and its French selection options. Later starts leave existing bases unchanged. FastAPI lives in `pinkbombs_api/`.

For the application, follow the doc below. For a server deployment, see [Staging and Production](#staging-and-production). The Python environment below is for development, not required for Docker startup.
Requirements:
- Docker Desktop (or Docker Engine with Compose v2 on Linux)
- OpenSSL. Python and Node are not required on the host to run the application.

### First Start

From the repository root:

```bash
bash nocodb/setup.sh
```

In the private, Git-ignored `nocodb/.env`, set `NOCODB_BOOTSTRAP_EMAIL` and `NOCODB_BOOTSTRAP_PASSWORD`. For a new installation these create the first administrator; for an existing installation use that administrator's credentials. Use a strong password. Then run:

```bash
bash nocodb/start.sh
```

Open NocoDB at [http://localhost:8080](http://localhost:8080) and sign in with those credentials. The `pinkbombs` base contains `reponses_pinkometre` and `consommations`. API documentation is at [http://localhost:8000/docs](http://localhost:8000/docs). Change `NOCODB_PORT` / `API_PORT` if necessary.

The stack runs NocoDB, its worker, PostgreSQL, Redis, and FastAPI. Only NocoDB and FastAPI bind to the host, on loopback. Browsers submit through FastAPI, never directly to PostgreSQL or NocoDB's write API.

### Restart and Initialization

Use the same `bash nocodb/start.sh` command for subsequent starts. Existing bases are **not migrated or repaired**: no column renames, option synchronization, view changes, grant changes, or member-role changes. Even an incomplete existing base is left untouched. Editing the schema file does not update an existing installation.

`start.sh` :
- starts NocoDB and the worker first
- runs the create-or-skip initializer
- builds/starts FastAPI.

Initialization or API failure returns a nonzero exit code but leaves NocoDB running for diagnosis.

Plain `docker compose up -d` only starts services; the initializer has a maintenance profile and never runs implicitly through Compose.

The initializer serializes setup with a PostgreSQL advisory lock. A new base is recorded as complete only after NocoDB record reads, schema guarantees, and API provisioning succeed. NocoDB metadata changes are not part of the SQL transaction: an interrupted install may leave a partial base, which requires explicit resume.

### Schema and Access

#### Data Model

[`nocodb/schema.json`](nocodb/schema.json) is the source of truth for the business columns, select options, and indexes:

- `reponses_pinkometre` stores one questionnaire response: optional email, impact levels, alternative, supplement, and omega-3 consent.
- `consommations` stores the consumption entries belonging to a response: scenario, product, variant, frequency, quantity, unit, and annual weight.

Each table has a generated `id`; NocoDB also supplies system timestamps such as UTC `created_at`. Only the response relation and `scenario` are required business fields. Email is optional and not unique. Decimal columns use `numeric(30,10)`, allowing up to 20 digits before and 10 after the decimal point.

Clients send English option codes, such as `initial`; FastAPI stores their French labels, such as `Initiale`. These are NocoDB SingleSelect fields backed by text and PostgreSQL CHECK constraints, not native PostgreSQL enum types. Neither IP addresses nor IP-derived fingerprints are stored in submissions.

#### Connection Identities

The NocoDB account and PostgreSQL roles are separate identities. Their settings live in the private `nocodb/.env`:

| Used By | Identity | Credentials | Purpose |
| --- | --- | --- | --- |
| NocoDB UI and initializer's metadata requests | NocoDB administrator account | `NOCODB_BOOTSTRAP_EMAIL` / `NOCODB_BOOTSTRAP_PASSWORD` | Sign in to the UI and create the base, tables, and relations. |
| NocoDB server and initializer's SQL provisioning | PostgreSQL administrator role `pinkbombs` | `POSTGRES_PASSWORD` | Manage NocoDB storage, database constraints, and API grants. |
| FastAPI | Dedicated PostgreSQL role from `API_DB_USER`, default **`pinkbombs_api`** | `API_DB_PASSWORD` | Insert submissions and manage retry keys using restricted permissions. |

**FastAPI connects directly to PostgreSQL as `API_DB_USER`.** It does not use the NocoDB administrator account or the PostgreSQL `pinkbombs` administrator role. Never set `API_DB_USER=pinkbombs`.

The default login role, Python package, and private SQL schema all happen to be named `pinkbombs_api`; they are different objects. Changing `API_DB_USER` changes the login name, not the package or SQL schema name.

#### FastAPI Permissions

The initializer creates or configures the dedicated API role with these permissions:

- **Submission tables:** `INSERT` on approved fields only and `SELECT(id)` so inserts can return generated IDs. Other submission fields cannot be read, and existing submissions cannot be updated or deleted by this role.
- **ID sequences and schemas:** `USAGE` to obtain generated IDs and access the managed schemas. The role cannot create tables in those schemas or grant access to others.
- **`pinkbombs_api.idempotency_keys`:** `SELECT`, `INSERT`, and `DELETE` to recognize retries and remove expired keys. This permission does not extend to the submission tables.

Provisioning rejects administrator privileges, role memberships, ownership, and excess effective access, including access inherited from `PUBLIC`. Password and grant changes are transactional and happen only during first initialization or explicit maintenance. Unrelated object grants are left untouched. If an administrator changes grants later, rerun explicit provisioning to verify them; `search_path` alone does not restrict access.

#### Initialization and Human Access

NocoDB's metadata API creates the tables, select options, and relations. SQL provisioning adds required constraints, decimal precision, foreign keys, and the declared indexes. Generated relation columns keep their NocoDB names; FastAPI discovers the physical foreign key from database constraints.

Normal startup leaves existing bases unchanged. It does not rename/delete columns, change options or grid views, or rewrite user permissions. New installations must have public base and view sharing disabled.

For collaborators, assign **viewer** access in NocoDB unless editing is intended. NocoDB administrators, workspace owners, and Docker operators remain privileged; the restricted FastAPI role does not limit their access.

### Submission API

The local API base URL is `http://localhost:8000`. The API binds to loopback by default; set `API_PORT` to change the host port. Configure `API_CORS_ORIGINS` in the private `nocodb/.env` with the exact frontend origins, then restart the stack. CORS is not authentication. The local Compose setup is not a public deployment: production use requires an HTTPS reverse proxy and a production API URL/origin.

- `GET /health`: process health check.
- `GET /ready`: PostgreSQL and Redis readiness check.
- `GET /api/v1/options`: canonical option codes and French labels from [`nocodb/schema.json`](nocodb/schema.json).
- `POST /api/v1/submissions`: validate and store one submission atomically.
- `GET /docs`: interactive API schema.

Send a UUID `Idempotency-Key` header on every submission. Reuse the same key when retrying the same payload: the API returns the original ID with `200` instead of inserting a duplicate. A different payload with the same key returns `409`. Idempotency records are retained for 24 hours.

Example request:

```json
{
    "response": {
        "email": "person@example.org",
        "impact_initial": "low",
        "impact_apres_engagement": "neutral",
        "alternative_choisie": "algae",
        "supplement_choisi": "chiaSeeds",
        "consentement_omega3": true
    },
    "consommations": [
        {
            "scenario": "initial",
            "produit": "fillet",
            "variante": "tranche",
            "frequence": "weekly",
            "occurence_par_an": 52,
            "quantite_par_occurrence": 0.15,
            "unite_fr": "portion",
            "poids_annuel_kg": 7.8
        },
        {
            "scenario": "afterCommitment",
            "produit": "pokeBowl",
            "unite_fr": "piece"
        }
    ]
}
```

`response` is required; its fields are optional. `consommations` must contain 1 to 100 rows. Each row requires `scenario`; other row fields are optional. Decimal values must be finite, nonnegative, and fit `numeric(30,10)`. Option fields use the stable codes from `GET /api/v1/options`, not their French labels. The server creates the parent relationship and database IDs; clients must not send IDs or extra fields. The API does not retain IP addresses or IP-derived fingerprints.

Success returns `201` with `{ "id": 123 }`; an identical retry returns `200` with the same body. Invalid input returns `422`, idempotency-key conflicts return `409`, rate limits return `429`, and unavailable persistence/rate limiting returns `503`. The default rate limit is 10 submissions per client per 60 seconds; tune `API_RATE_LIMIT` and `API_RATE_WINDOW_SECONDS` in `.env` as needed.

### Diagnostics and Recovery

Run the read-only check from the repository root:

```bash
bash nocodb/check.sh
docker compose -f nocodb/compose.yaml logs --tail=100 nocodb worker api
```

The check verifies schema metadata, reads both tables through NocoDB, and checks the completion record. It never calls bootstrap or changes grants. An older installation can work without the new completion record; review it before adopting it through explicit provisioning.

If tables appear but rows fail with `Please check server log for more details`, inspect NocoDB logs. A missing generated foreign-key column indicates an older SQL rename left metadata out of sync. Restarting the application does not repair that inconsistency.

After backup and review, these commands are available from `nocodb/`:

```bash
# Resume an interrupted first install: create missing tables/relations, verify, provision.
docker compose run --rm --no-deps schema-init resume

# Adopt an already compatible base or refresh API credentials/grants explicitly.
docker compose run --rm --no-deps schema-init provision
docker compose up -d --force-recreate api
```

Neither command renames/drops columns, rewrites options, or fixes corrupt NocoDB metadata. Incompatible existing definitions fail instead of being overwritten. Metadata changes persist if a later SQL step fails; the SQL provisioning transaction rolls back. To discard a disposable local installation instead, follow the reset instructions below.

### Delete or Recreate a Local Database

A **NocoDB base** is the collection of tables shown in the UI. The PostgreSQL database stores those tables alongside NocoDB accounts and metadata. Docker's named **volumes** retain PostgreSQL data, attachments, and Redis state after containers stop.

**Both workflows below are destructive. Back up anything you need first. Use them only for disposable local data, never staging or production.** Run all commands from the repository root and check that they target the intended Compose project.

#### Delete Only the Managed Base

Use this when you want to discard the questionnaire tables but keep your NocoDB account, other bases, credentials, and Docker volumes.

1. Stop FastAPI so no new submissions arrive during deletion:

    ```bash
    docker compose -f nocodb/compose.yaml stop api
    ```

2. Sign in to NocoDB as administrator. Find the base configured by `NOCODB_BASE_NAME` (default `pinkbombs`), open its menu/settings, choose **Delete base**, and confirm. This removes that base and its submission data. Do not delete only its tables: an existing empty base is still skipped by normal startup.

3. For an initialized installation, clear the managed API's old retry keys so they cannot return IDs from deleted submissions:

    ```bash
    docker compose -f nocodb/compose.yaml exec -T db \
      psql -U pinkbombs -d pinkbombs -v ON_ERROR_STOP=1 \
      -c 'TRUNCATE TABLE pinkbombs_api.idempotency_keys;'
    ```

    This deletes all retry keys for this stack's managed API, not other bases' submission rows. If initialization never created this table, skip this step. An old installation-completion row may remain; the new base gets a different ID and does not reuse it.

4. Recreate the missing base and verify it:

    ```bash
    bash nocodb/start.sh
    bash nocodb/check.sh
    ```

Do not drop the underlying PostgreSQL database or manually delete NocoDB's physical tables for a base-only reset; that can leave its metadata inconsistent.

#### Wipe the Entire Local Stack

**This deletes every database and NocoDB account in this Compose stack, all submissions, attachments, retry keys, and Redis state.** It preserves the private `nocodb/.env` file, but none of the data in the stack's named volumes.

```bash
docker compose -f nocodb/compose.yaml down --volumes
bash nocodb/start.sh
bash nocodb/check.sh
```

On the empty storage, startup creates a new administrator from `NOCODB_BOOTSTRAP_EMAIL` / `NOCODB_BOOTSTRAP_PASSWORD` and initializes the base again. Existing `.env` credentials are preserved, not regenerated. In contrast, ordinary `docker compose down` (without `--volumes`) keeps your data and is not a reset.

### Staging and Production

This runbook describes the Debian 13 deployment on the Hostinger VPS `72.61.97.142`. The frontend is hosted separately on Vercel. One Traefik instance terminates HTTPS for both backend environments using its **file provider**, not Docker labels or the Docker socket. Server configuration files below are created manually; the application scripts do not install Traefik.

| Setting | Staging | Production |
| --- | --- | --- |
| Repository directory | `/opt/pinkbombs/12_pinkbombs` | `/opt/pinkbombs/production` |
| Git branch | `dev` | `main` |
| Compose project | `pinkbombs` | `pinkbombs-production` |
| Frontend origin | `https://dev.pinkbombs.org` | `https://pinkbombs.org` |
| API URL | `https://dev-api.pinkbombs.org` | `https://api.pinkbombs.org` |
| NocoDB URL | `https://dev-nocodb.pinkbombs.org` | `https://nocodb.pinkbombs.org` |
| Loopback API / NocoDB ports | `8000` / `8080` | `8001` / `8081` |
| NocoDB access | Traefik BasicAuth, then NocoDB login | NocoDB login only |

Each application project has its own database, Redis, attachments, secrets, default network, and API image. Only API and NocoDB join the shared proxy network. A shared host/proxy is not strong isolation against a compromised host. **Never rename an initialized Compose project or copy staging secrets/volumes into production.**

#### 1. Server, DNS, and Firewall Prerequisites

Run commands individually on the server and stop at the first failure. Docker Engine and the Compose plugin must be installed before proceeding; the deployed VPS came with Docker preinstalled. Check `docker --version`, `docker compose version`, `ss -ltnp`, `ip -4 route`, `docker network ls`, `free -h`, and `df -h /`. Install supporting tools:

```bash
apt-get update
apt-get install -y dnsutils curl ca-certificates openssl apache2-utils git
```

Determine the active DNS provider before editing records:

```bash
dig +trace pinkbombs.org NS
```

The domain delegates to `dns105.ovh.net` and `ns105.ovh.net`: **edit the OVH zone**, not Hostinger's inactive DNS editor. Add these A records pointing to `72.61.97.142`: `dev-api`, `dev-nocodb`, `api`, and `nocodb`. DNS names contain neither `https://` nor a trailing slash. Preserve the existing frontend and email records. Do not add AAAA records unless IPv6 is configured. Do not change nameservers or create child nameservers to add application subdomains.

Verify each hostname, first against the authority and then a public resolver; substitute the other three names:

```bash
dig @dns105.ovh.net dev-api.pinkbombs.org A
dig @1.1.1.1 dev-api.pinkbombs.org A
dig @1.1.1.1 dev-api.pinkbombs.org AAAA
```

In the Hostinger VPS firewall, allow inbound TCP 80/443 publicly and the actual SSH port, currently 22; restrict SSH sources where practical. Deny other unsolicited inbound traffic while permitting required outbound traffic. Do not publicly open 8000/8001, 8080/8081, 5432, or 6379. Preserve Docker-managed firewall rules. Keep the current SSH session open and verify a **second SSH connection** after firewall activation.

#### 2. Prepare the Shared Proxy Once

Skip creation if this infrastructure already exists; inspect it rather than overwriting it. Check routes and existing Docker subnets before choosing this network range. Reserve `172.30.50.2` for Traefik outside Docker's automatic allocation range:

```bash
docker network create --driver bridge --subnet 172.30.50.0/24 --ip-range 172.30.50.128/25 --gateway 172.30.50.1 traefik_proxy
install -d -m 700 /opt/traefik /opt/traefik/dynamic /opt/traefik/secrets /opt/traefik/letsencrypt
htpasswd -cB /opt/traefik/secrets/nocodb.htpasswd staging-admin
chmod 600 /opt/traefik/secrets/nocodb.htpasswd
touch /opt/traefik/letsencrypt/acme.json
chmod 600 /opt/traefik/letsencrypt/acme.json
```

Enter a unique staging gateway password at the prompt, not in shell history. `htpasswd -c` is for a **new file only**; omit `-c` to update an existing file. `touch` preserves existing ACME state: never truncate/delete it as a renewal strategy.

Create `/opt/traefik/compose.yaml`:

```yaml
name: pinkbombs-edge
services:
    traefik:
        image: traefik:v3.7.15
        restart: unless-stopped
        command:
            - --entrypoints.web.address=:80
            - --entrypoints.websecure.address=:443
            - --entrypoints.web.http.redirections.entrypoint.to=websecure
            - --entrypoints.web.http.redirections.entrypoint.scheme=https
            - --entrypoints.web.http.aliasheadersstrategy=reject
            - --entrypoints.websecure.http.aliasheadersstrategy=reject
            - --providers.file.directory=/etc/traefik/dynamic
            - --providers.file.watch=true
            - --certificatesresolvers.letsencrypt.acme.email=info@seastemik.org
            - --certificatesresolvers.letsencrypt.acme.storage=/letsencrypt/acme.json
            - --certificatesresolvers.letsencrypt.acme.httpchallenge.entrypoint=web
            - --log.level=INFO
        ports:
            - "80:80"
            - "443:443"
        volumes:
            - ./dynamic:/etc/traefik/dynamic:ro
            - ./secrets:/secrets:ro
            - ./letsencrypt:/letsencrypt
        networks:
            proxy:
                ipv4_address: 172.30.50.2
        logging:
            driver: json-file
            options:
                max-size: "10m"
                max-file: "3"
networks:
    proxy:
        external: true
        name: traefik_proxy
```

This pins the version used for deployment; review supported security updates before a new rollout. HTTP-01 requires public port 80 and works with HTTPS redirection. Standard Let's Encrypt issuance requires no mailbox verification. Use a team-approved contact address; keep certificate monitoring separate from email reminders. The configuration exposes no dashboard and mounts no Docker socket.

#### 3. Clone and Initialize Each Environment Privately

Before production initialization, verify that reviewed fixes tested on `dev` have been released to `main` using [Release Dev to Main](#release-dev-to-main). File presence alone does not prove that `main` contains the current initializer.

For a new server checkout, use the appropriate command below. Do not clone over an existing directory or move a running staging checkout:

```bash
git clone --branch dev --single-branch https://github.com/dataforgoodfr/12_pinkbombs.git /opt/pinkbombs/12_pinkbombs
git clone --branch main --single-branch https://github.com/dataforgoodfr/12_pinkbombs.git /opt/pinkbombs/production
```

Deploy **one environment at a time**. Enter its `nocodb` directory, clear shell-level overrides from the other environment, then generate its private configuration:

```bash
cd /opt/pinkbombs/12_pinkbombs/nocodb
unset COMPOSE_FILE COMPOSE_PROJECT_NAME
bash setup.sh
```

For production, use `cd /opt/pinkbombs/production/nocodb` instead. Edit that directory's `.env`; set `NOCODB_BOOTSTRAP_EMAIL` and a new strong `NOCODB_BOOTSTRAP_PASSWORD`. Preserve setup-generated secrets and the pinned `NOCODB_IMAGE`. Do not source the environment file, commit it, or paste it into logs/chat. Use these environment-specific settings:

| Variable | Staging | Production |
| --- | --- | --- |
| `COMPOSE_PROJECT_NAME` | `pinkbombs` | `pinkbombs-production` |
| `COMPOSE_FILE` during private initialization | `compose.yaml` | `compose.yaml` |
| `API_PORT` | `8000` | `8001` |
| `NOCODB_PORT` | `8080` | `8081` |
| `NC_SITE_URL` | `https://dev-nocodb.pinkbombs.org` | `https://nocodb.pinkbombs.org` |
| `API_CORS_ORIGINS` | `https://dev.pinkbombs.org` | `https://pinkbombs.org` |
| `FORWARDED_ALLOW_IPS` | `172.30.50.2` | `172.30.50.2` |

Origins have no trailing slash. Include `https://www.pinkbombs.org` only if that is an actual frontend browser origin; it differs from the apex origin. The same internal `NOCODB_BASE_NAME=pinkbombs` and database role names are safe because storage is separate. `FORWARDED_ALLOW_IPS` trusts only the reserved proxy, never `*` or the server's public IP.

From the selected `nocodb` directory, validate and initialize before publishing any route:

```bash
docker compose config --quiet
docker compose config --format json | grep '"name":'
bash start.sh
bash check.sh
docker compose ps
```

Confirm the top-level project name and container prefixes match the selected environment. The check must report `PASS`. Verify localhost readiness at `http://127.0.0.1:8000/ready` for staging or `http://127.0.0.1:8001/ready` for production. Do not continue on failure. Setup already runs inside `start.sh`; from `nocodb/`, the command is `bash setup.sh`, not `bash nocodb/setup.sh`.

#### 4. Attach the Application to Traefik

Create `compose.traefik.yaml` inside each environment's `nocodb` directory. For staging:

```yaml
services:
    api:
        networks:
            default: {}
            proxy:
                aliases: [pinkbombs-staging-api]
    nocodb:
        networks:
            default: {}
            proxy:
                aliases: [pinkbombs-staging-nocodb]
networks:
    proxy:
        external: true
        name: traefik_proxy
```

For production, use the same content but replace the two aliases with `pinkbombs-production-api` and `pinkbombs-production-nocodb`. Aliases are internal Docker DNS names, not public DNS records. Only API/NocoDB join `proxy`; both retain `default` for database/Redis access. Host ports stay loopback-only. Container ports remain 8000/8080 in both environments.

In **each private `.env`**, change `COMPOSE_FILE` to `compose.yaml:compose.traefik.yaml` for persistent selection. Keep the project name unchanged. Then, from that environment's `nocodb` directory:

```bash
unset COMPOSE_FILE COMPOSE_PROJECT_NAME
docker compose config --quiet
bash start.sh
bash check.sh
docker network inspect traefik_proxy --format '{{range .Containers}}{{println .Name}}{{end}}'
```

Only Traefik and the two environments' API/NocoDB containers should appear on the proxy network. These starts briefly recreate changed containers but preserve data. For maintenance, always enter the intended `nocodb` directory: scripts resolve `COMPOSE_FILE` there. Passing only `-f compose.yaml` overrides that selection and omits the proxy override. Keep `.env` and server-specific overrides out of commits.

#### 5. Publish HTTPS Routes

Create `/opt/traefik/dynamic/pinkbombs.yaml` for staging and the shared minimum TLS policy:

```yaml
http:
    routers:
        pinkbombs-staging-api:
            rule: "Host(`dev-api.pinkbombs.org`)"
            entryPoints: [websecure]
            service: pinkbombs-staging-api
            tls: {certResolver: letsencrypt}
        pinkbombs-staging-nocodb:
            rule: "Host(`dev-nocodb.pinkbombs.org`)"
            entryPoints: [websecure]
            service: pinkbombs-staging-nocodb
            middlewares: [team-access]
            tls: {certResolver: letsencrypt}
    services:
        pinkbombs-staging-api:
            loadBalancer:
                servers: [{url: "http://pinkbombs-staging-api:8000"}]
        pinkbombs-staging-nocodb:
            loadBalancer:
                servers: [{url: "http://pinkbombs-staging-nocodb:8080"}]
    middlewares:
        team-access:
            basicAuth:
                usersFile: /secrets/nocodb.htpasswd
                removeHeader: true
tls:
    options:
        default:
            minVersion: VersionTLS12
```

Only publish an environment after its private initialization passes. For production, create a **separate** `/opt/traefik/dynamic/pinkbombs-production.yaml`:

```yaml
http:
    routers:
        pinkbombs-production-api:
            rule: "Host(`api.pinkbombs.org`)"
            entryPoints: [websecure]
            service: pinkbombs-production-api
            tls: {certResolver: letsencrypt}
        pinkbombs-production-nocodb:
            rule: "Host(`nocodb.pinkbombs.org`)"
            entryPoints: [websecure]
            service: pinkbombs-production-nocodb
            tls: {certResolver: letsencrypt}
    services:
        pinkbombs-production-api:
            loadBalancer:
                servers: [{url: "http://pinkbombs-production-api:8000"}]
        pinkbombs-production-nocodb:
            loadBalancer:
                servers: [{url: "http://pinkbombs-production-nocodb:8080"}]
```

Production intentionally has **no BasicAuth middleware**, but still requires NocoDB account authentication. Do not remove staging's middleware or duplicate the shared default TLS policy. Disable public base/view sharing and review account/signup permissions before admitting real data; use least-privilege collaborator accounts rather than sharing the bootstrap administrator.

For the first proxy startup, validate and start explicitly:

```bash
docker compose -p pinkbombs-edge -f /opt/traefik/compose.yaml config --quiet
docker compose -p pinkbombs-edge -f /opt/traefik/compose.yaml up -d
docker compose -p pinkbombs-edge -f /opt/traefik/compose.yaml logs --tail=100 traefik
```

For an existing proxy, new dynamic files reload automatically; no restart is needed. Changes to the proxy's Compose/static configuration require validation and `up -d` again. Compose validation does not validate routing files: inspect provider/ACME logs and actual endpoints. Never paste ACME state or password hashes into diagnostics.

#### 6. Verify Each Deployment

Run these from a separate machine, not only from the server:

```bash
curl -fsS https://dev-api.pinkbombs.org/ready
curl -fsS https://api.pinkbombs.org/ready
curl -I http://api.pinkbombs.org/ready
curl -I https://dev-nocodb.pinkbombs.org/
curl -I https://nocodb.pinkbombs.org/
```

Both APIs must return `{"status":"ready"}` with valid trusted certificates; HTTP must redirect to HTTPS. Staging NocoDB returns `401` and a BasicAuth challenge. Production NocoDB must have no `WWW-Authenticate: Basic` challenge; a native login page/redirect is expected. Confirm both environments' table grids in the browser. Do not use `curl -k` to bypass certificate failures.

Verify production CORS without writing a submission; repeat with staging's API/frontend origins:

```bash
curl -i -X OPTIONS https://api.pinkbombs.org/api/v1/submissions \
    -H 'Origin: https://pinkbombs.org' \
    -H 'Access-Control-Request-Method: POST' \
    -H 'Access-Control-Request-Headers: content-type,idempotency-key'
```

Expect HTTP 200 and the exact allowed origin, method, and headers. Other origins must not receive permission. CORS is not authentication. Configure each frontend to use its matching API URL, never NocoDB or database credentials; redeploy the frontend if environment values are build-time. Test one synthetic browser submission (`201`, or `200` for an identical retry), confirm it appears only in the intended database, and check independent client-IP rate limiting. Keep staging free of production personal data.

#### Release Dev to Main

Test and validate changes in staging first. Prefer a reviewed GitHub pull request with **base `main`, compare `dev`**, and passing CI. This promotes code only, not staging data or private configuration.

If direct merges are permitted, run locally on your development machine, **not the production server**. Start with a clean worktree and stop on errors:

```bash
git status --short
git fetch origin
git switch main
git pull --ff-only origin main
git log --oneline main..origin/dev
git merge origin/dev
poetry run pre-commit run --all-files
```

Resolve conflicts and complete the merge before checks. Review/commit any formatter changes and rerun required checks and affected integration tests until they pass. Then run `git push origin main` and confirm CI passes before production rollout. If `main` is protected, use the pull request workflow instead. Do not rebase or force-push a deployed branch. Production's `git pull` cannot promote changes that have not been published to `main`.

#### Update an Existing Deployment

Run commands individually and stop at the first failure. Updating changed containers can briefly interrupt service. For staging, select `/opt/pinkbombs/12_pinkbombs/nocodb` and branch `dev`; for production, release to `main` first and select `/opt/pinkbombs/production/nocodb`.

1. Enter the intended directory. Clear stale shell overrides with `unset COMPOSE_FILE COMPOSE_PROJECT_NAME`; the private `.env` must retain its correct project and both Compose files. Run `git status --short`, `git branch --show-current`, and `git rev-parse HEAD`. Preserve local configuration and record the previous revision.
2. Back up PostgreSQL, NocoDB attachments, private `.env`/override files, and shared Traefik configuration, authentication, and certificate storage. Coordinate database/attachment backups by quiescing writes where necessary. Store encrypted copies off-server and test restores separately. Review schema/image changes before proceeding. A production **database-only** snapshot is:

     ```bash
     umask 077
     install -d -m 700 /var/backups/pinkbombs-production
     backup_dir=$(mktemp -d /var/backups/pinkbombs-production/predeploy.XXXXXXXX)
     docker compose exec -T db pg_dump -U pinkbombs -d pinkbombs -Fc > "$backup_dir/database.dump"
     ```

     Stop if the dump fails. Use a distinct staging backup destination when working on staging. This snapshot alone does not back up attachments/configuration and is not an off-server backup.
3. For production, run the following from its `nocodb` directory. For staging, substitute `git pull --ff-only origin dev` and its public readiness URL:

     ```bash
     git pull --ff-only origin main
     docker compose config --quiet
     bash start.sh
     bash check.sh
     curl -fsS https://api.pinkbombs.org/ready
     ```

4. Verify affected browser/submission workflows and the other environment's readiness. Application pulls do not update the separate Traefik configuration or guarantee a Vercel frontend redeployment. Keep server-specific files private and preserve the pinned NocoDB image until a separately tested upgrade is approved.
5. Existing-base startup does **not** apply schema migrations or refresh grants/passwords. Use reviewed, backed-up explicit maintenance for those changes. If rollout fails, stop and inspect logs; reverting code may not reverse database changes. Plan rollback against the recorded revision and tested backup, without blind hard resets.

**Never use `docker compose down --volumes` or `down -v` for deployment updates.** They delete accounts, submissions, attachments, and Redis state for the selected project. A disposable first-install reset is a separate destructive recovery decision, never a routine fix. Do not regenerate existing secrets or change project names to resolve startup failures. Before admitting real traffic, establish automated off-server backups/restore tests, certificate/uptime alerts, and disk/log monitoring.

#### Deployment Troubleshooting

| Symptom | Check and Action |
| --- | --- |
| DNS edits have no effect | Check `dig +trace pinkbombs.org NS`. Edit the authoritative OVH zone, not the hosting provider's inactive zone. Do not migrate nameservers without preserving all website/email records. |
| `dig +short` returns nothing | Run the full query to distinguish NXDOMAIN, no A record, and SERVFAIL. Query the authoritative server and a public resolver. Check exact names, conflicting A/CNAME/AAAA records, publication and negative caching. |
| Hostinger firewall activation is unauthorized | Reauthenticate or ask the VPS owner/support to check permissions. SSH root access does not grant hosting-panel privileges. Do not flush Docker firewall tables. |
| Compose cannot find configuration or targets another stack | Enter the correct `nocodb` directory and inspect project/container names. Clear inherited Compose variables and verify the private `.env`. An explicit `-f compose.yaml` omits the proxy override. |
| Containers/networks appear missing | Check `docker context show`, `docker ps -a`, and `docker network ls` before recreating anything. Confirm the intended Docker daemon, project, and existing volumes. |
| Pull says up to date but production lacks a fix | `main` may not contain tested `dev` changes. Review/release `dev` to `main`, then fast-forward production. Do not copy individual files from staging. |
| Pull refuses to fast-forward | Inspect branch history and local modifications; rewritten history needs explicit reconciliation. Do not force-pull, hard-reset, or delete server configuration. |
| Database authentication fails | Environment changes do not update initialized PostgreSQL role passwords. Restore matching credentials or perform a controlled rotation. Database container health does not verify the API role. |
| Bootstrap signin returns HTTP 400 | Use the credentials of the existing NocoDB account. Bootstrap environment variables do not reset its password; test via the UI/private SSH tunnel. |
| API `/ready` returns 503 | Run `bash check.sh` and `docker compose logs --tail=100 api db nocodb`. A missing `pinkbombs_api` role indicates incomplete provisioning, not merely a wrong password. Diagnose before creating roles or running maintenance. |
| Initializer reports a physical foreign-key rename failure, or table reads return 500 | Verify the released initializer version and compare NocoDB metadata with physical columns. The old initializer could leave a partial/inconsistent base. Updated startup skips existing bases; neither `resume` nor `provision` repairs corrupt metadata. Back up and review recovery; never blindly rename generated columns or reset live data. |
| HTTPS fails or Traefik returns 502 | Inspect edge logs, A/AAAA and CAA records, port 80/443 ingress, ACME permissions, proxy membership, and exact aliases/container ports. Traefik's localhost is not the application's localhost. Preserve certificate state and do not bypass TLS verification. |
| NocoDB returns 401 before its login page | Expected only for staging's BasicAuth gateway. Use `staging-admin` first, then the separate staging NocoDB account. Production should require only its native account login; check router middleware if it shows the extra prompt. |
| Browser fails while curl succeeds | Check the actual browser origin, frontend API URL, and POST preflight for Content-Type/Idempotency-Key. Apex and `www` origins differ. Frontend configuration changes may require redeployment. |
| All clients share one rate-limit bucket | Verify the API trusts only Traefik's reserved address via `FORWARDED_ALLOW_IPS` and that requests traverse that proxy. Never set unrestricted forwarded-header trust to bypass the symptom. |

### Tests

Install dependencies with `poetry install`, then run:

```bash
poetry run pytest tests/test_submission_api.py tests/test_submission_postgres.py
node --test nocodb/test-bootstrap.mjs
```

The Python PostgreSQL integration tests skip unless `TEST_DATABASE_URL` points to a disposable PostgreSQL database named `test_*`; they create and remove temporary schemas and a temporary restricted role.

The JavaScript privilege regression suite exercises the actual bootstrap provisioner on PostgreSQL 17 or later. Set `TEST_DATABASE_URL` to a **separate disposable `test_*` database**, not the deployment database, with a superuser connection for role, ownership, and session-authorization tests. It refuses an existing `pinkbombs_api` schema and rolls back all fixtures. In the NocoDB container runtime, run:

```bash
cd nocodb
docker compose run --rm --no-deps -e TEST_DATABASE_URL --entrypoint node schema-init --test /bootstrap/test-provision-postgres.mjs
```

The test database must be reachable from that container. Alternatively, with `knex` and `pg` available to Node locally, run `node --test nocodb/test-provision-postgres.mjs` from the repository root. Without `TEST_DATABASE_URL`, this suite skips; a skip does not validate PostgreSQL privilege behavior.

The NocoDB integration check is read-only:

```bash
cd nocodb
docker compose run --rm --no-deps --entrypoint node schema-init /bootstrap/integration-test.mjs
```

### Operations

Use these commands for everyday management. From the repository root, first enter the Compose directory:

```bash
cd nocodb
```

For staging/production, persist `COMPOSE_FILE=compose.yaml:compose.traefik.yaml` in the selected server's private `nocodb/.env` as described above. Enter that environment's `nocodb` directory and clear stale shell-level Compose overrides when switching environments. Use the same Compose project and configuration that you used to start the application.

| Task | Command | What It Does |
| --- | --- | --- |
| Start the application | `bash start.sh` | Starts services, creates the base only if missing, and builds/starts FastAPI. Existing bases are left unchanged. |
| Check which services are running | `docker compose ps` | Shows container status, health, and published ports. Does not change anything. |
| Check the database setup | `bash check.sh` | Checks the expected schema, NocoDB table/grid reads, and initialization completion. Does not change stored data. |
| Read recent application errors | `docker compose logs --tail=100 nocodb worker api` | Shows the last 100 log lines for each listed service. |
| Watch logs live | `docker compose logs --follow --tail=100 nocodb worker api` | Streams new log lines. Press `Ctrl+C` to stop watching; services keep running. |
| Stop the application | `docker compose down` | Stops and removes this project's containers and network, but preserves data in named volumes. |

**Stopping is not deleting.** After `docker compose down`, your database, NocoDB accounts, and attachments remain. Run `bash start.sh` from this directory to start again with the same data. To intentionally erase local data, follow [Delete or Recreate a Local Database](#delete-or-recreate-a-local-database); do not add `--volumes` or `-v` during a normal shutdown.

Before upgrades or recovery, back up PostgreSQL, NocoDB attachments, and the private `.env` file outside the repository. Keep the pinned `NOCODB_IMAGE` unchanged until you have checked NocoDB's [self-hosting guidance](https://nocodb.com/docs/self-hosting) and tested the upgrade in staging.

Application submissions should go through FastAPI, not direct PostgreSQL inserts. Graph generation and its dependencies are independent of the API container.

