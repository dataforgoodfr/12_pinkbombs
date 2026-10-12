#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
bash setup.sh
docker compose up -d --wait --wait-timeout 240 db redis nocodb
docker compose run --rm --no-deps schema-init
docker compose up -d --wait --wait-timeout 120 worker api
printf '%s\n' 'Pinkometre schema initialized; submission API is ready. Local API port: API_PORT in .env.'