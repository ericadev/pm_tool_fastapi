#!/usr/bin/env sh
set -e

echo "Running database migrations..."
alembic upgrade head

echo "Starting API server..."
echo "Port is ${PORT:?PORT environment variable is not set}"
exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT" --log-level info
