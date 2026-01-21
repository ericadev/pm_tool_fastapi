#!/usr/bin/env sh
set -ex

echo "=== ENTRYPOINT START ==="

# Check for PORT (Railway injects it for services)
: "${PORT:?PORT environment variable is not set. Did you deploy as a Service?}"

echo "PORT is: $PORT"

if [ ! -d "app" ]; then
  echo "ERROR: app/ directory not found. Exiting."
  exit 1
fi

echo "=== Running database migrations ==="
python migrate.py
echo "=== Starting FastAPI server ==="
exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT"