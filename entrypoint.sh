#!/bin/sh

echo "Waiting for postgres..."

while ! nc -z db 5432; do
  sleep 0.1
done

echo "PostgreSQL started"

echo "Initializing database..."
python -m src.init_db

echo "Seeding database..."
python -m src.seed_db

echo "Starting application..."
exec uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
