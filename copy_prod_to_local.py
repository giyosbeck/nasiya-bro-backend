#!/usr/bin/env python3
"""
Script to run on PRODUCTION SERVER to copy database to local machine.
This script creates a database backup and transfers it to local machine.
"""

import os
import subprocess
import sys
from datetime import datetime

# Production database configuration (local on prod server)
PROD_HOST = "localhost"  # Running on prod server, so localhost
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
    print("🔄 Creating production database backup on server...")
    
    # Get production database password
    prod_password = input("Enter production database password: ")
    if not prod_password:
        print("❌ Password is required")
        sys.exit(1)
    
    # Get target local machine details
    local_user = input("Enter your local machine username: ")
    local_host = input("Enter your local machine IP/hostname: ")
    
    if not local_user or not local_host:
        print("❌ Local machine details required")
        sys.exit(1)
    
    # Create timestamp for backup file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"nasiya_backup_{timestamp}.sql"
    
    print("\n1️⃣ Creating database backup...")
    
    # Set environment for production backup
    prod_env = os.environ.copy()
    prod_env['PGPASSWORD'] = prod_password
    
    # Create backup with complete data
    backup_cmd = f"pg_dump -h {PROD_HOST} -p {PROD_PORT} -U {PROD_USER} -d {PROD_DB} --no-owner --no-privileges --clean --if-exists --verbose > {backup_file}"
    
    if not run_command(backup_cmd, env=prod_env):
        print("❌ Failed to create backup")
        sys.exit(1)
    
    print(f"✅ Backup created: {backup_file}")
    
    # Check backup file size
    try:
        file_size = os.path.getsize(backup_file)
        print(f"📁 Backup file size: {file_size / 1024 / 1024:.2f} MB")
    except:
        pass
    
    print("\n2️⃣ Compressing backup...")
    
    # Compress the backup
    compress_cmd = f"gzip {backup_file}"
    if run_command(compress_cmd):
        backup_file = f"{backup_file}.gz"
        print(f"✅ Backup compressed: {backup_file}")
    
    print("\n3️⃣ Transferring to local machine...")
    
    # Transfer to local machine via SCP
    transfer_cmd = f"scp {backup_file} {local_user}@{local_host}:~/nasiya_backup.sql.gz"
    
    if not run_command(transfer_cmd):
        print("❌ Failed to transfer backup")
        print(f"📋 You can manually copy: {backup_file}")
        print(f"📋 To your local machine and run:")
        print(f"📋   gunzip ~/nasiya_backup.sql.gz")
        print(f"📋   createdb nasiya_bro")
        print(f"📋   psql -d nasiya_bro < ~/nasiya_backup.sql")
    else:
        print("✅ Backup transferred to local machine")
        
        print("\n4️⃣ Creating restore instructions...")
        
        # Create restore script for local machine
        restore_script = f"""#!/bin/bash
# Run this script on your LOCAL MACHINE to restore the database

echo "🔄 Setting up local database from production backup..."

# Get local PostgreSQL password
read -s -p "Enter local PostgreSQL password: " LOCAL_PASSWORD
echo

export PGPASSWORD=$LOCAL_PASSWORD

# Drop existing database if it exists
echo "Dropping existing database..."
dropdb -h localhost -U postgres --if-exists nasiya_bro

# Create new database
echo "Creating database..."
createdb -h localhost -U postgres nasiya_bro

# Decompress and restore
echo "Restoring backup..."
gunzip -c ~/nasiya_backup.sql.gz | psql -h localhost -U postgres -d nasiya_bro

# Create .env file
echo "Creating .env file..."
cat > .env << EOF
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
echo "🔧 Local database: postgresql://postgres:***@localhost:5432/nasiya_bro"
echo "📁 Environment file created: .env"
"""
        
        with open('restore_local_db.sh', 'w') as f:
            f.write(restore_script)
        
        # Make restore script executable
        os.chmod('restore_local_db.sh', 0o755)
        
        # Transfer restore script
        transfer_script_cmd = f"scp restore_local_db.sh {local_user}@{local_host}:~/"
        if run_command(transfer_script_cmd):
            print("✅ Restore script transferred")
            
            print(f"\n🎉 Production database backup completed!")
            print(f"📦 Files transferred to {local_user}@{local_host}:")
            print(f"   • ~/nasiya_backup.sql.gz")
            print(f"   • ~/restore_local_db.sh")
            print(f"\n📋 Run on your LOCAL MACHINE:")
            print(f"   cd ~/your-project-backend/")
            print(f"   bash ~/restore_local_db.sh")
        
    # Clean up local backup files
    cleanup = input("\nDelete backup files from server? (y/N): ").lower().strip()
    if cleanup == 'y':
        try:
            os.remove(backup_file)
            if os.path.exists('restore_local_db.sh'):
                os.remove('restore_local_db.sh')
            print("🗑️ Server backup files deleted")
        except:
            print("⚠️ Could not delete some files")
    else:
        print(f"📦 Server files preserved: {backup_file}")

if __name__ == "__main__":
    main()