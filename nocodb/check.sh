#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
docker compose ps
docker compose run --rm --no-deps --entrypoint node schema-init /bootstrap/integration-test.mjs