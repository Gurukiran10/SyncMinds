#!/bin/bash
# Start the Meeting Intelligence backend for local development
set -a
# Export each line of .env that has KEY=VALUE (skip comments and blanks)
while IFS= read -r line; do
  [[ "$line" =~ ^#.*$ ]] && continue
  [[ -z "$line" ]] && continue
  [[ "$line" == *"="* ]] && export "$line" 2>/dev/null || true
done < "$(dirname "$0")/.env"
set +a

# Defaults for missing vars
export SENTRY_DSN="${SENTRY_DSN:-}"
export OPENAI_API_KEY="${OPENAI_API_KEY:-dummy}"

cd "$(dirname "$0")"
exec python3 -m uvicorn app.main:app --host "${HOST:-0.0.0.0}" --port "${PORT:-8002}" "$@"
