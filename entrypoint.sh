#!/bin/bash
set -e

echo "Waiting for PostgreSQL..."
until python -c "
from sqlalchemy import create_engine, text
import os
e = create_engine(os.environ['POSTGRES_DB_URI'])
with e.connect() as c:
    c.execute(text('SELECT 1'))
" 2>/dev/null; do
    sleep 1
done
echo "PostgreSQL is ready."

echo "Running migrations..."
alembic -c app/alembic.ini upgrade head

echo "Populating lottery data..."
python -m app.scripts.lotto_data

echo "Starting API server..."
uvicorn app:app --host 0.0.0.0 --port 8000
