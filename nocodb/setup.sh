#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if [[ -e .env ]]; then
    command -v openssl >/dev/null
    chmod 600 .env
    if ! grep -q '^API_PORT=' .env; then
        printf '\n%s\n' 'API_PORT=8000' >> .env
    fi
    if ! grep -q '^API_DB_USER=' .env; then
        printf '%s\n' 'API_DB_USER=pinkbombs_api' >> .env
    fi
    if ! grep -q '^API_DB_PASSWORD=' .env; then
        printf '%s\n' "API_DB_PASSWORD=Aa1!$(openssl rand -hex 32)" >> .env
    fi
    if ! grep -q '^API_IDEMPOTENCY_SECRET=' .env; then
        printf '%s\n' "API_IDEMPOTENCY_SECRET=$(openssl rand -hex 32)" >> .env
    fi
    if ! grep -q '^API_RATE_LIMIT_SECRET=' .env; then
        printf '%s\n' "API_RATE_LIMIT_SECRET=$(openssl rand -hex 32)" >> .env
    fi
    if ! grep -q '^API_CORS_ORIGINS=' .env; then
        printf '%s\n' 'API_CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173' >> .env
    fi
    if ! grep -q '^API_RATE_LIMIT=' .env; then
        printf '%s\n' 'API_RATE_LIMIT=10' >> .env
    fi
    if ! grep -q '^API_RATE_WINDOW_SECONDS=' .env; then
        printf '%s\n' 'API_RATE_WINDOW_SECONDS=60' >> .env
    fi
    printf '%s\n' 'Existing credentials preserved; missing API settings generated.'
    exit 0
fi

command -v openssl >/dev/null
umask 077
postgres_password="$(openssl rand -hex 32)"
jwt_secret="$(openssl rand -hex 32)"
api_db_password="Aa1!$(openssl rand -hex 32)"
api_idempotency_secret="$(openssl rand -hex 32)"
api_rate_limit_secret="$(openssl rand -hex 32)"
set -o noclobber
sed \
    -e "s/GENERATE_POSTGRES_PASSWORD/${postgres_password}/" \
    -e "s/GENERATE_JWT_SECRET/${jwt_secret}/" \
    -e "s/GENERATE_API_DB_PASSWORD/${api_db_password}/" \
    -e "s/GENERATE_API_IDEMPOTENCY_SECRET/${api_idempotency_secret}/" \
    -e "s/GENERATE_API_RATE_LIMIT_SECRET/${api_rate_limit_secret}/" \
    .env.example > .env
printf '%s\n' 'Created private nocodb/.env. Configure bootstrap credentials, then run: bash nocodb/start.sh'