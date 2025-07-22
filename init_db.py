#!/usr/bin/env python3
"""
Database initialization script for HMIS Backend
This script creates all tables and populates them with seed data
"""

from app import app, db
import os

def init_database():
    """Initialize the database by creating all tables"""
    print("Initializing HMIS database...")
    
    with app.app_context():
        # Remove existing database if it exists
        if os.path.exists('hmis.db'):
            os.remove('hmis.db')
            print("Removed existing database")
        
        # Create all tables
        db.create_all()
        print("Created all database tables")
        
        # Import and run seed data
        print("Loading seed data...")
        exec(open('seed.py').read())
        
        print("✅ Database initialized successfully!")
        print("You can now run the application with: python app.py")
        print("\nDefault users:")
        print("- admin / password123 (Admin)")
        print("- doctor1 / password123 (Doctor)")
        print("- nurse1 / password123 (Nurse)")
        print("- it1 / password123 (IT)")
        print("- labtech1 / password123 (Lab Tech)")

if __name__ == '__main__':
    init_database()