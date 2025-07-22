#!/usr/bin/env python3
"""
Database reset script for HMIS Backend
This script removes the existing database and creates a fresh one
"""

import os
from init_db import init_database

def reset_database():
    """Reset the database by removing it and creating a fresh one"""
    print("🔄 Resetting HMIS database...")
    
    # Confirm action
    response = input("Are you sure you want to reset the database? This will delete all data! (y/N): ")
    if response.lower() != 'y':
        print("Database reset cancelled.")
        return
    
    # Remove existing database
    if os.path.exists('hmis.db'):
        os.remove('hmis.db')
        print("Removed existing database")
    
    # Initialize fresh database
    init_database()

if __name__ == '__main__':
    reset_database()