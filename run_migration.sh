#!/bin/bash

# Nasiya Bro PostgreSQL Migration Script
# This script automates the entire migration process

set -e  # Exit on any error

echo "=========================================="
echo "Nasiya Bro PostgreSQL Migration"
echo "=========================================="

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "Error: PostgreSQL is not installed or not in PATH"
    echo "Please install PostgreSQL first:"
    echo "  macOS: brew install postgresql"
    echo "  Ubuntu: sudo apt-get install postgresql postgresql-contrib"
    echo "  CentOS: sudo yum install postgresql postgresql-server"
    exit 1
fi

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Install PostgreSQL requirements
echo "Installing PostgreSQL requirements..."
python3 -m pip install --upgrade pip
python3 -m pip install psycopg2-binary --no-cache-dir || python3 -m pip install psycopg2 || echo "Trying alternative..."
python3 -m pip install asyncpg sqlalchemy

# Make migration script executable
chmod +x migrate_to_postgresql.py

# Run the migration
echo "Starting migration process..."
python3 migrate_to_postgresql.py

echo "=========================================="
echo "Migration completed!"
echo "You can now start your backend with:"
echo "python3 run.py"
echo "=========================================="