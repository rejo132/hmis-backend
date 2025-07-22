#!/bin/bash

# HMIS Backend Setup Script
echo "Setting up HMIS Backend..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Set environment variables
export FLASK_APP=app.py
export FLASK_ENV=development

# Run database migrations
echo "Setting up database..."
flask db upgrade

# Seed database
echo "Seeding database with initial data..."
python seed.py

echo "Setup complete!"
echo ""
echo "To start the server, run:"
echo "source venv/bin/activate && export FLASK_APP=app.py && flask run"
echo ""
echo "Test users:"
echo "- Admin: username=admin, password=password123"
echo "- Doctor: username=doctor1, password=password123"  
echo "- Nurse: username=nurse1, password=password123"
echo "- IT: username=it1, password=password123"
echo "- Lab Tech: username=labtech1, password=password123"