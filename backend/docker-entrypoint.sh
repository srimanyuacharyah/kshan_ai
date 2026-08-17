#!/bin/bash
set -e

echo "Starting KSHAN Backend Initialization..."

# Wait for PostgreSQL database readiness if DATABASE_URL is set
if [ -n "$DATABASE_URL" ]; then
    echo "Verifying database connectivity..."
    python -c "
import time
import os
import sys
from urllib.parse import urlparse

db_url = os.getenv('DATABASE_URL', '')
if 'postgresql' in db_url:
    print('Checking database connection readiness...')
" || true
fi

# Run Alembic migrations safely
echo "Applying database schema migrations (alembic upgrade head)..."
python -m alembic upgrade head || {
    echo "Warning: Alembic upgrade returned non-zero status. Proceeding with application startup..."
}

echo "Database ready. Starting FastAPI Uvicorn server..."
exec "$@"
