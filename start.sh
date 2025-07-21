#!/bin/bash

# HMIS Backend Startup Script

echo "Starting HMIS Backend..."

# Activate virtual environment
source venv/bin/activate

# Check if database exists, if not initialize it
if [ ! -f "hmis.db" ]; then
    echo "Database not found. Initializing..."
    python seed.py
fi

# Start the application
echo "Starting Flask application on http://0.0.0.0:5000"
python run.py