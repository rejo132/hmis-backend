#!/bin/bash

echo "Setting up PostgreSQL for HMIS Backend..."

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "PostgreSQL is not installed. Please install it first:"
    echo "Ubuntu/Debian: sudo apt update && sudo apt install postgresql postgresql-contrib"
    echo "macOS: brew install postgresql"
    echo "Then run this script again."
    exit 1
fi

# Check if PostgreSQL service is running
if ! pg_isready &> /dev/null; then
    echo "Starting PostgreSQL service..."
    sudo systemctl start postgresql || sudo service postgresql start
fi

# Create database and user
echo "Creating database and user..."
sudo -u postgres createdb hmis_db 2>/dev/null || echo "Database hmis_db already exists"
sudo -u postgres createuser hmis_user 2>/dev/null || echo "User hmis_user already exists"

# Set password and grant privileges
sudo -u postgres psql -c "ALTER USER hmis_user WITH PASSWORD 'hmis_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE hmis_db TO hmis_user;"
sudo -u postgres psql -d hmis_db -c "GRANT ALL ON SCHEMA public TO hmis_user;"
sudo -u postgres psql -d hmis_db -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO hmis_user;"

# Create .env file
echo "Creating .env file..."
cat > .env << 'EOF'
DATABASE_URL=postgresql://hmis_user:hmis_password@localhost:5432/hmis_db
FLASK_ENV=development
JWT_SECRET_KEY=your-local-development-secret-key
SECRET_KEY=your-local-development-secret-key
EOF

# Install Python dependencies if venv exists
if [ -d "venv" ]; then
    echo "Installing Python dependencies..."
    source venv/bin/activate
    pip install psycopg2-binary
    
    # Run migrations
    echo "Running database migrations..."
    export FLASK_APP=app.py
    flask db upgrade
    
    # Seed database
    echo "Seeding database..."
    python seed.py
    
    echo "Setup complete!"
    echo ""
    echo "You can now run: flask run"
    echo ""
    echo "Test login credentials:"
    echo "- Username: admin"
    echo "- Password: password123"
else
    echo "Virtual environment not found. Please create one first:"
    echo "python3 -m venv venv"
    echo "source venv/bin/activate"
    echo "pip install -r requirements.txt"
    echo "Then run this script again."
fi