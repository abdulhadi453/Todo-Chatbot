#!/bin/bash
# Todo Backend API Startup Script for Unix/Linux

echo "Starting Todo Backend API Setup..."

# Load environment variables
echo "Loading environment variables..."
if [ -f .env ]; then
    export $(cat .env | xargs)
fi

# Install dependencies
echo "Installing required packages..."
pip install -r backend/requirements.txt

# Initialize database
echo "Initializing database..."
python -c "from backend.config.database import create_db_and_tables; create_db_and_tables(); print('Database initialized successfully!')"

# Start the server
echo "Starting the Todo Backend API server..."
uvicorn backend.src.main:app --host ${API_HOST:-0.0.0.0} --port ${API_PORT:-8000} --reload

echo "Server stopped."