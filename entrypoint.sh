#!/usr/bin/env sh
set -ex

echo "=== ENTRYPOINT START ==="

# Check for PORT (Railway injects it for services)
: "${PORT:?PORT environment variable is not set. Did you deploy as a Service?}"

echo "PORT is: $PORT"

# Optional: check that required directories exist
if [ ! -f "alembic.ini" ]; then
  echo "ERROR: alembic.ini not found in /app. Exiting."
  exit 1
fi

if [ ! -d "app" ]; then
  echo "ERROR: app/ directory not found. Exiting."
  exit 1
fi

echo "=== Running database migrations ==="
alembic upgrade head || {
  echo "ERROR: Alembic migrations failed!"
  exit 1
}

echo "=== Listing project files for debugging ==="
ls -R

echo "=== Starting FastAPI server ==="
exec uvicorn app.main:app \
  --host 0.0.0.0 \
  --port "$PORT" \
  --reload \
  --log-level debug
