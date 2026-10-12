Pinkbombs
================


This repository contains the data tools behind the [Pinkbombs website](https://www.pinkbombs.org):

- Local data management with NocoDB and PostgreSQL for the Pinkometre.
- CSV preparation, translation, and download packaging.
- Python generation of interactive graphs and maps.

The managed NocoDB startup initializes the Pinkometre tables and their French selection options without importing submissions or CSV data. The Python visualization scripts still read the CSV files in `data/`; starting NocoDB does not automatically connect those scripts to the database.

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

## To launch pre-commits locally

[Install precommit](https://pre-commit.com/)

    pre-commit run --all-files 
 
## Test the code with Tox

    tox -vv

## How to
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


## Local NocoDB

The local Docker Compose stack runs NocoDB, its worker, PostgreSQL, and Redis. The Pinkometre schema is initialized automatically; no submission data is imported.

### Start

Install Docker Desktop, then run from the repository root:

```bash
bash nocodb/setup.sh
```

Add your existing NocoDB administrator credentials as `NOCODB_BOOTSTRAP_EMAIL` and `NOCODB_BOOTSTRAP_PASSWORD` in the Git-ignored `nocodb/.env`. Keep that file private. Start or restart the managed stack with:

```bash
bash nocodb/start.sh
```

Open [http://localhost:8080](http://localhost:8080). The service is bound to localhost; PostgreSQL and Redis are not exposed to the host. Change `NOCODB_PORT` in `.env` if needed. Always use `start.sh` so schema initialization runs; existing records are preserved, and incompatible schema changes fail rather than deleting data.

The FastAPI submission service is included in the local Compose stack and starts after the Pinkometre schema is initialized. PostgreSQL and Redis remain private to Compose. NocoDB is used to view and maintain the data; browser submissions go through FastAPI and never connect directly to PostgreSQL or NocoDB's write API.

### Schema and access

[`nocodb/schema.json`](nocodb/schema.json) defines the two tables, exact French select labels, and English application-code mappings:

- `reponses_pinkometre`: generated `id`, UTC creation time (`created_at` in PostgreSQL), optional email and HMAC, impacts, alternative, supplement, and omega-3 consent.
- `consommations`: generated `id`, required response relation and `scenario`, product, optional variant, frequency, annual occurrence count, quantity, unit, and annual weight.

Only the response relation and `scenario` are required. The annual frequency is decimal. Email and HMAC are not unique; raw IP addresses must never be stored. The initializer uses NocoDB's API for metadata and schema-only SQL migrations for the foreign key, select checks, and nonunique indexes. It disables public sharing for the base and views.

The administrator is reserved for maintenance. Bootstrap makes all other direct base members viewers. FastAPI uses a separate PostgreSQL role limited to inserting approved fields and reading generated IDs; it cannot read, update, or delete submission rows. Workspace owners, administrators, and Docker operators can override NocoDB permissions.

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

`response` is required; its fields are optional. `consommations` must contain 1 to 100 rows. Each row requires `scenario`; other row fields are optional. Decimal values must be finite, nonnegative, and fit `numeric(30,10)`. Option fields use the stable codes from `GET /api/v1/options`, not their French labels. The server creates the parent relationship and database IDs; clients must not send IDs, `empreinte_ip_hmac`, or extra fields. The server does not store raw IP addresses.

Success returns `201` with `{ "id": 123 }`; an identical retry returns `200` with the same body. Invalid input returns `422`, idempotency-key conflicts return `409`, rate limits return `429`, and unavailable persistence/rate limiting returns `503`. The default rate limit is 10 submissions per client per 60 seconds; tune `API_RATE_LIMIT` and `API_RATE_WINDOW_SECONDS` in `.env` as needed.

### API checks

Install dependencies with `poetry install`, then run:

```bash
poetry run pytest tests/test_submission_api.py tests/test_submission_postgres.py
node --test nocodb/test-bootstrap.mjs
```

The PostgreSQL integration tests skip unless `TEST_DATABASE_URL` points to a disposable PostgreSQL database named `test_*`; they create and remove temporary schemas and a temporary restricted role. The NocoDB integration check is read-only:

```bash
cd nocodb
docker compose run --rm --no-deps --entrypoint node schema-init /bootstrap/integration-test.mjs
```

### Operations

From `nocodb/`:

```bash
docker compose ps
docker compose logs --tail=100 nocodb worker
curl -fsS http://localhost:8080/api/v1/health
docker compose down
```

Named volumes retain database and attachment data after `down`. Never use `down -v` unless you intend to delete that data. Back up PostgreSQL, attachments, and `.env` outside the repository before upgrades or recovery. Change the pinned `NOCODB_IMAGE` only after checking NocoDB's [self-hosting guidance](https://nocodb.com/docs/self-hosting).

Run the schema unit tests with `node --test nocodb/test-bootstrap.mjs`. Do not insert or update submissions directly in PostgreSQL; use the FastAPI submission endpoint.
