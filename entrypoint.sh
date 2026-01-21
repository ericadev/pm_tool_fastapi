#!/usr/bin/env sh
set -ex

# Force unbuffered output
export PYTHONUNBUFFERED=1

echo "=== ENTRYPOINT START ===" >&2

# Check for PORT (Railway injects it for services)
: "${PORT:?PORT environment variable is not set. Did you deploy as a Service?}"

echo "PORT is: $PORT" >&2

if [ ! -d "app" ]; then
  echo "ERROR: app/ directory not found. Exiting." >&2
  exit 1
fi

echo "=== Running database migrations ===" >&2
python migrate.py
echo "=== Starting FastAPI server ===" >&2
exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT"