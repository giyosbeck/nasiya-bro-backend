#!/bin/bash
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
psql -h localhost -U postgres -d nasiya_bro < nasiya_prod_dump_20250913_134351.sql

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
