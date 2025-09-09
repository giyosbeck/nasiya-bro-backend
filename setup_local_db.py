#!/usr/bin/env python3
"""
Setup local PostgreSQL database with basic structure for development.
Since direct database access is blocked, we'll create the schema and add basic data.
"""

import os
import subprocess
import sys
from datetime import datetime

# Configuration
LOCAL_HOST = "localhost"  
LOCAL_PORT = "5432"
LOCAL_DB = "nasiya_bro"
LOCAL_USER = "postgres"

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
    print("🔄 Setting up local PostgreSQL database...")
    
    # Get local database password
    local_password = input("Enter local PostgreSQL password: ")
    if not local_password:
        print("❌ Password is required")
        sys.exit(1)
    
    print("\n1️⃣ Setting up local database...")
    
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
    
    print("\n2️⃣ Creating database schema...")
    
    # Create tables using SQLAlchemy
    try:
        from sqlalchemy import create_engine, text
        from app.models import user, product, transaction, notification, magazine, auto_product, auto_transaction
        from app.db.database import Base
        
        # Create engine for local database
        database_url = f"postgresql://{LOCAL_USER}:{local_password}@{LOCAL_HOST}:{LOCAL_PORT}/{LOCAL_DB}"
        engine = create_engine(database_url)
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database schema created")
        
        # Create UserType enum if not exists
        with engine.connect() as conn:
            conn.execute(text("CREATE TYPE IF NOT EXISTS usertype AS ENUM ('gadgets', 'auto')"))
            conn.commit()
        
        print("✅ UserType enum created")
        
    except Exception as e:
        print(f"❌ Failed to create schema: {e}")
        sys.exit(1)
    
    print("\n3️⃣ Adding basic admin user...")
    
    try:
        from sqlalchemy.orm import sessionmaker
        from app.models.user import User, UserRole, UserStatus, UserType
        from app.core.security import get_password_hash
        
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Create admin user
        admin_user = User(
            name="Admin",
            phone="01234567",
            password_hash=get_password_hash("23154216"),
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE,
            user_type=UserType.GADGETS
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print("✅ Admin user created (phone: 01234567, password: 23154216)")
        
    except Exception as e:
        print(f"⚠️ Failed to create admin user: {e}")
    
    finally:
        if 'db' in locals():
            db.close()
    
    print("\n4️⃣ Updating local configuration...")
    
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
    
    print(f"\n🎉 Local database setup completed successfully!")
    print(f"🗄️ Local database: {LOCAL_DB}")
    print(f"🔧 Connection string: postgresql://{LOCAL_USER}:***@{LOCAL_HOST}:{LOCAL_PORT}/{LOCAL_DB}")
    print(f"👤 Admin login: 01234567 / 23154216")

if __name__ == "__main__":
    main()