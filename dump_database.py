#!/usr/bin/env python3
"""
Script to run on PRODUCTION SERVER to create database dump.
Creates a SQL dump file that can be uploaded to GitHub and downloaded locally.
"""

import os
import subprocess
import sys
from datetime import datetime

# Production database configuration (local on prod server)
PROD_HOST = "localhost"  # Running on prod server
PROD_PORT = "5432"
PROD_DB = "nasiya_bro" 
PROD_USER = "nasiya_user"

def run_command(command, env=None):
    """Run shell command and return success status"""
    try:
        print(f"Running: {command}")
        result = subprocess.run(command, shell=True, check=True, env=env)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: Command failed with exit code {e.returncode}")
        return False

def main():
    print("🔄 Creating production database dump...")
    
    # Get production database password
    prod_password = input("Enter production database password: ")
    if not prod_password:
        print("❌ Password is required")
        sys.exit(1)
    
    # Create timestamp for dump file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dump_file = f"nasiya_prod_dump_{timestamp}.sql"
    
    print("\n1️⃣ Creating database dump...")
    
    # Set environment for production dump
    prod_env = os.environ.copy()
    prod_env['PGPASSWORD'] = prod_password
    
    # Create clean dump with complete data
    dump_cmd = f"pg_dump -h {PROD_HOST} -p {PROD_PORT} -U {PROD_USER} -d {PROD_DB} --no-owner --no-privileges --clean --if-exists --verbose > {dump_file}"
    
    if not run_command(dump_cmd, env=prod_env):
        print("❌ Failed to create dump")
        sys.exit(1)
    
    print(f"✅ Database dump created: {dump_file}")
    
    # Check dump file size
    try:
        file_size = os.path.getsize(dump_file)
        print(f"📁 Dump file size: {file_size / 1024 / 1024:.2f} MB")
        
        if file_size > 100 * 1024 * 1024:  # 100MB
            print("⚠️  Large file - consider compressing before upload")
    except:
        pass
    
    print("\n2️⃣ Creating restore script...")
    
    # Create restore script for local machine
    restore_script = f"""#!/bin/bash
# Run this script on LOCAL MACHINE to restore the database

echo "🔄 Restoring production database dump to local PostgreSQL..."

# Get local PostgreSQL password
read -s -p "Enter local PostgreSQL password: " LOCAL_PASSWORD
echo

export PGPASSWORD=$LOCAL_PASSWORD

# Drop existing database if it exists
echo "Dropping existing nasiya_bro database..."
dropdb -h localhost -U postgres --if-exists nasiya_bro

# Create new database
echo "Creating nasiya_bro database..."
createdb -h localhost -U postgres nasiya_bro

# Restore dump
echo "Restoring database from dump..."
psql -h localhost -U postgres -d nasiya_bro < {dump_file}

# Create .env file for local development
echo "Creating .env file..."
cat > .env << 'EOF'
DATABASE_URL=postgresql://postgres:$LOCAL_PASSWORD@localhost:5432/nasiya_bro
PROJECT_NAME=Nasiya Bro API
VERSION=1.0.0
API_V1_STR=/api/v1
SECRET_KEY=nasiya-bro-secret-key-2025-change-in-production-please
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=11520
DEFAULT_ADMIN_USERNAME=01234567
DEFAULT_ADMIN_PASSWORD=23154216
UPLOAD_FOLDER=uploads
MAX_FILE_SIZE=10485760
TIMEZONE=Asia/Tashkent
EOF

echo "✅ Database restored successfully!"
echo "🔧 Connection: postgresql://postgres:***@localhost:5432/nasiya_bro"
echo "📁 Environment file: .env"
echo "🚀 You can now run: python run.py"
"""
    
    restore_file = "restore_from_dump.sh"
    with open(restore_file, 'w') as f:
        f.write(restore_script)
    
    # Make restore script executable
    os.chmod(restore_file, 0o755)
    
    print(f"✅ Restore script created: {restore_file}")
    
    print(f"\n🎉 Database dump completed!")
    print(f"📦 Files created:")
    print(f"   • {dump_file} - Database dump")
    print(f"   • {restore_file} - Restore script")
    
    print(f"\n📋 Next steps:")
    print(f"1. Upload both files to GitHub")
    print(f"2. Download on local machine")
    print(f"3. Run: bash {restore_file}")

if __name__ == "__main__":
    main()