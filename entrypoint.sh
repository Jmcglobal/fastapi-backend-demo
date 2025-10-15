#!/bin/bash
set -e

echo "Starting FastAPI Application..."

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
until PGPASSWORD=admin1234 psql -h postgres -U admin -d fastapi -c '\q' 2>/dev/null; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 2
done

echo "PostgreSQL is up - executing migrations"

# Change to app directory
cd /app

# Run database migrations
echo "Running Alembic migrations..."
alembic upgrade head

echo "Migrations completed successfully!"

# Change to src directory
# cd /app/src

# Start the application
echo "Starting Uvicorn server..."
exec uvicorn src.main:app --host 0.0.0.0 --port 8000
