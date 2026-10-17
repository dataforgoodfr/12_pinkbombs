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

Traefik terminates HTTPS and routes requests to NocoDB and FastAPI. The example below assumes an existing Traefik instance with its Docker provider enabled, a `websecure` entrypoint, a certificate resolver named `letsencrypt`, and an external Docker network shared with the application. Adapt those names to your Traefik configuration; this repository does not deploy Traefik itself.

#### Environment and Routing

1. Run `bash nocodb/setup.sh` on the server. Give staging and production separate Compose projects, volumes, secrets, hostnames, and Traefik router names. Use separate deployment directories and set a unique `COMPOSE_PROJECT_NAME` in each private `nocodb/.env`; never copy local database volumes or commit credentials.
2. Set strong bootstrap credentials, `NC_SITE_URL=https://nocodb.example.org`, and `API_CORS_ORIGINS=https://your-frontend.example.org`. Configure the frontend to submit to the HTTPS API hostname, not NocoDB. Set `NOCODB_BASE_NAME` if needed.
3. Attach **only `nocodb` and `api`** to Traefik's existing external network, keeping them on the application's default network too. PostgreSQL, Redis, the worker, and the initializer stay on the default network. Do not expose PostgreSQL or Redis through Traefik.
4. Configure two HTTPS routers:

| Router | Host Rule | Container Port | Access |
| --- | --- | --- | --- |
| NocoDB | ``Host(`nocodb.example.org`)`` | `8080` | Team-only, protected by your Traefik authentication or IP-allowlist middleware. |
| Submission API | ``Host(`api.example.org`)`` | `8000` | Frontend submissions; apply appropriate request limits. CORS is not authentication. |

Traefik must route to the **container ports**, not the published localhost ports. A Traefik container's `127.0.0.1` refers to Traefik itself. Set `traefik.docker.network` to the actual external network name so the Docker provider selects the correct network. Traefik forwards Host/scheme headers and supports NocoDB WebSocket upgrades without a separate WebSocket router.

#### Compose Override

Keep local development unchanged by placing the server-specific configuration in `nocodb/compose.traefik.yaml`. This example uses the external network `traefik_proxy`; Traefik must already be attached to it. Replace the hostnames, network, resolver, and team-access middleware with your deployment values:

```yaml
services:
    nocodb:
        networks: [default, proxy]
        labels:
            - traefik.enable=true
            - traefik.docker.network=traefik_proxy
            - traefik.http.routers.${COMPOSE_PROJECT_NAME}-nocodb.rule=Host(`nocodb.example.org`)
            - traefik.http.routers.${COMPOSE_PROJECT_NAME}-nocodb.entrypoints=websecure
            - traefik.http.routers.${COMPOSE_PROJECT_NAME}-nocodb.tls.certresolver=letsencrypt
            - traefik.http.routers.${COMPOSE_PROJECT_NAME}-nocodb.middlewares=team-access@file
            - traefik.http.routers.${COMPOSE_PROJECT_NAME}-nocodb.service=${COMPOSE_PROJECT_NAME}-nocodb
            - traefik.http.services.${COMPOSE_PROJECT_NAME}-nocodb.loadbalancer.server.port=8080
    api:
        networks: [default, proxy]
        labels:
            - traefik.enable=true
            - traefik.docker.network=traefik_proxy
            - traefik.http.routers.${COMPOSE_PROJECT_NAME}-api.rule=Host(`api.example.org`)
            - traefik.http.routers.${COMPOSE_PROJECT_NAME}-api.entrypoints=websecure
            - traefik.http.routers.${COMPOSE_PROJECT_NAME}-api.tls.certresolver=letsencrypt
            - traefik.http.routers.${COMPOSE_PROJECT_NAME}-api.service=${COMPOSE_PROJECT_NAME}-api
            - traefik.http.services.${COMPOSE_PROJECT_NAME}-api.loadbalancer.server.port=8000
networks:
    default: {}
    proxy:
        external: true
        name: traefik_proxy
```

`team-access@file` is a placeholder for a middleware you define in Traefik's file provider; it is not created by this application. Use your existing team-access middleware, including its provider suffix. Set Traefik's Docker provider to `exposedByDefault=false` so unlabeled services stay private.

The original host-port bindings remain loopback-only and are not used by Traefik. If both environments share a server, assign different `NOCODB_PORT` and `API_PORT` values to avoid host-port collisions, even though their container ports stay the same.

#### Proxy Trust and Startup

Set `FORWARDED_ALLOW_IPS` in the private environment file to Traefik's IP address on the shared network. For stable trust, reserve that address in your Traefik/network configuration; use comma-separated addresses for multiple trusted proxies. Do not use `*` or trust arbitrary clients. Without this setting, FastAPI sees the proxy as the client, so submissions share its rate-limit bucket instead of being limited per client.

From the repository root, select both Compose files before invoking the scripts:

```bash
export COMPOSE_FILE=compose.yaml:compose.traefik.yaml
bash nocodb/start.sh
bash nocodb/check.sh
```

These scripts change into `nocodb/`, so the exported file paths are relative to that directory. Keep the same `COMPOSE_FILE` selection for subsequent starts and maintenance. For direct Compose commands, first `cd nocodb` and use that environment; passing only `-f compose.yaml` omits the Traefik override.

Point both hostnames' DNS records at Traefik, verify TLS issuance and HTTP-to-HTTPS redirection in your Traefik configuration, then check the API's HTTPS `/ready` endpoint and open both NocoDB tables through the protected hostname. Verify that forwarded client addresses produce the expected API rate limiting. The local check verifies application health, not Traefik routing, certificates, or access controls.

Back up PostgreSQL, NocoDB attachments and `.env` before deployment changes. Test restores in an isolated environment. Keep the pinned `NOCODB_IMAGE` digest; test upgrades and schema changes on a restored staging database first. Existing-base startup intentionally does not apply schema upgrades. Never run `docker compose down -v` against staging/production.

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

For staging/production, keep `COMPOSE_FILE=compose.yaml:compose.traefik.yaml` exported as described above so every command uses the Traefik configuration too. Use the same Compose project and environment that you used to start the application.

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

