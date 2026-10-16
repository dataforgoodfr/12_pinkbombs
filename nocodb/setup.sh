#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

command -v openssl >/dev/null
umask 077
touch .env
chmod 600 .env
while IFS='=' read -r key value || [[ -n "$key" ]]; do
    [[ -z "$key" || "$key" == \#* ]] && continue
    grep -q "^${key}=" .env && continue
    if [[ "$value" == GENERATE_* ]]; then
        value="$(openssl rand -hex 32)"
    fi
    printf '\n%s=%s\n' "$key" "$value" >> .env
done < .env.example
printf '%s\n' 'Private nocodb/.env is ready; existing values preserved. Set bootstrap credentials, then run: bash nocodb/start.sh'