#!/usr/bin/env python3
"""
Script to copy production database to local PostgreSQL for development.
This script will:
1. Create a backup of the production database
2. Create a new local database 
3. Restore the backup to the local database
"""

import os
import subprocess
import sys
from datetime import datetime

# Configuration - Using production database from remote server
PROD_HOST = "nasiya.backend.leadai.uz"
PROD_PORT = "5432"
PROD_DB = "nasiya_bro"  # Based on microservices config
PROD_USER = "nasiya_user"  # Based on microservices config

LOCAL_HOST = "localhost"  
LOCAL_PORT = "5432"
LOCAL_DB = "nasiya_bro"  # Match production database name
LOCAL_USER = "postgres"  # Local PostgreSQL user

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
    print("🔄 Starting production database copy process...")
    
    # Get production database password
    prod_password = input("Enter production database password: ")
    if not prod_password:
        print("❌ Password is required")
        sys.exit(1)
    
    # Get local database password (if different)
    local_password = input("Enter local database password (press Enter if same as prod): ")
    if not local_password:
        local_password = prod_password
    
    # Create timestamp for backup file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"nasiya_backup_{timestamp}.sql"
    
    print("\n1️⃣ Creating production database backup...")
    
    # Set environment for production backup
    prod_env = os.environ.copy()
    prod_env['PGPASSWORD'] = prod_password
    
    backup_cmd = f"pg_dump -h {PROD_HOST} -p {PROD_PORT} -U {PROD_USER} -d {PROD_DB} --no-owner --no-privileges --clean --if-exists > {backup_file}"
    
    if not run_command(backup_cmd, env=prod_env):
        print("❌ Failed to create backup")
        sys.exit(1)
    
    print(f"✅ Backup created: {backup_file}")
    
    print("\n2️⃣ Setting up local database...")
    
    # Set environment for local database
    local_env = os.environ.copy()
    local_env['PGPASSWORD'] = local_password
    
    # Drop existing local database if it exists
    drop_cmd = f"dropdb -h {LOCAL_HOST} -p {LOCAL_PORT} -U {LOCAL_USER} --if-exists {LOCAL_DB}"
    run_command(drop_cmd, env=local_env)
    
    # Create new local database
    create_cmd = f"createdb -h {LOCAL_HOST} -p {LOCAL_PORT} -U {LOCAL_USER} {LOCAL_DB}"
    if not run_command(create_cmd, env=local_env):
        print("❌ Failed to create local database")
        sys.exit(1)
    
    print("✅ Local database created")
    
    print("\n3️⃣ Restoring backup to local database...")
    
    restore_cmd = f"psql -h {LOCAL_HOST} -p {LOCAL_PORT} -U {LOCAL_USER} -d {LOCAL_DB} < {backup_file}"
    if not run_command(restore_cmd, env=local_env):
        print("❌ Failed to restore backup")
        sys.exit(1)
    
    print("✅ Backup restored to local database")
    
    print("\n4️⃣ Updating local database connection...")
    
    # Create .env file for local development
    env_content = f"""# Local Development Database Configuration
DATABASE_URL=postgresql://{LOCAL_USER}:{local_password}@{LOCAL_HOST}:{LOCAL_PORT}/{LOCAL_DB}
PROJECT_NAME=Nasiya Bro API
VERSION=1.0.0
API_V1_STR=/api/v1

# Security
SECRET_KEY=nasiya-bro-secret-key-2025-change-in-production-please
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=11520

# Admin credentials 
DEFAULT_ADMIN_USERNAME=01234567
DEFAULT_ADMIN_PASSWORD=23154216

# File upload
UPLOAD_FOLDER=uploads
MAX_FILE_SIZE=10485760

# Timezone
TIMEZONE=Asia/Tashkent
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Created .env file with local database configuration")
    
    print(f"\n🎉 Database copy completed successfully!")
    print(f"📁 Backup file: {backup_file}")
    print(f"🗄️ Local database: {LOCAL_DB}")
    print(f"🔧 Connection string: postgresql://{LOCAL_USER}:***@{LOCAL_HOST}:{LOCAL_PORT}/{LOCAL_DB}")
    
    # Clean up backup file option
    cleanup = input("\nDelete backup file? (y/N): ").lower().strip()
    if cleanup == 'y':
        os.remove(backup_file)
        print(f"🗑️ Deleted {backup_file}")
    else:
        print(f"📦 Backup file preserved: {backup_file}")

if __name__ == "__main__":
    main()