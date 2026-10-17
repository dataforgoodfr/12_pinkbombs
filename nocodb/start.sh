#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
bash setup.sh
docker compose up -d --wait --wait-timeout 240 db redis nocodb worker
if ! docker compose run --rm --no-deps schema-init start; then
	printf '%s\n' 'Initialization failed. NocoDB is still running. Run: bash nocodb/check.sh' >&2
	exit 1
fi
if ! docker compose up -d --build --wait --wait-timeout 120 api; then
	printf '%s\n' 'NocoDB is running; the API is not ready. Run: bash nocodb/check.sh' >&2
	exit 1
fi
printf '%s\n' 'NocoDB and the submission API are ready. Host ports: NOCODB_PORT and API_PORT in nocodb/.env.'