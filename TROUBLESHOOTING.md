# HMIS Backend Troubleshooting Guide

## Common Issues and Solutions

### 1. Database Table Errors

**Error:** `sqlite3.OperationalError: no such table: user`

**Solution:**
```bash
# Initialize the database
python init_db.py

# Or reset if already exists
python reset_db.py
```

**Why this happens:** The database tables haven't been created yet.

### 2. Migration Conflicts

**Error:** `KeyError: 'password_hash'` or migration failures

**Solution:**
```bash
# Use the init script instead of migrations
python init_db.py
```

**Why this happens:** There are conflicting migration files from development.

### 3. Missing Dependencies

**Error:** `ModuleNotFoundError: No module named 'flask'`

**Solution:**
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Port Already in Use

**Error:** `Address already in use`

**Solution:**
```bash
# Find process using port 5000
lsof -i :5000

# Kill the process
kill -9 <PID>

# Or use a different port
PORT=5001 python app.py
```

### 5. JWT Token Issues

**Error:** `Bad Authorization header`

**Solution:**
- Make sure to include the token in the Authorization header
- Format: `Authorization: Bearer <your-jwt-token>`
- Get a fresh token by logging in again

### 6. CORS Issues

**Error:** `CORS policy: No 'Access-Control-Allow-Origin' header`

**Solution:**
- The app is configured for `http://localhost:3000`
- If using a different frontend URL, update the CORS config in `app.py`

### 7. Permission Denied

**Error:** `Permission denied` when running scripts

**Solution:**
```bash
# Make scripts executable
chmod +x start.sh
chmod +x init_db.py
chmod +x reset_db.py
```

## Quick Fixes

### Reset Everything
```bash
# Complete reset
rm -f hmis.db
python init_db.py
```

### Check Application Status
```bash
# Test health endpoint
curl http://localhost:5000/health

# Test login
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password123"}'
```

### Development Setup
```bash
# Quick development setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python init_db.py
python app.py
```

## Need Help?

1. Check that all dependencies are installed
2. Ensure the virtual environment is activated
3. Verify the database is initialized
4. Check the application logs for specific errors
5. Try resetting the database if all else fails

## Useful Commands

```bash
# Start application
python app.py

# Initialize database
python init_db.py

# Reset database
python reset_db.py

# Run with startup script
./start.sh

# Check database tables
sqlite3 hmis.db ".tables"

# Check users in database
sqlite3 hmis.db "SELECT * FROM user;"
```