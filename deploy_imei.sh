#!/bin/bash
"""
IMEI Migration Deployment Script
Upload and run this on your production server
"""

echo "🚀 Deploying IMEI Migration to Production"
echo "========================================"

# Check if we're in the right directory
if [ ! -f "app/main.py" ]; then
    echo "❌ Error: Please run this from the backend directory"
    echo "   Expected: /path/to/backend/"
    echo "   Current:  $(pwd)"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ] && [ ! -d ".venv" ] && [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Warning: No virtual environment detected"
    echo "📦 Installing dependencies globally..."
    pip install sqlalchemy psycopg2-binary
fi

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "🔧 Activating virtual environment..."
    source venv/bin/activate
elif [ -d ".venv" ]; then
    echo "🔧 Activating virtual environment..."
    source .venv/bin/activate
fi

# Install required dependencies
echo "📦 Installing migration dependencies..."
pip install sqlalchemy psycopg2-binary

# Run the migration
echo "🚀 Running IMEI migration..."
python deploy_imei_migration.py

# Check if migration was successful
if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 IMEI Migration Deployed Successfully!"
    echo "✅ Backend models updated"
    echo "✅ Database schema updated"
    echo "✅ API endpoints ready"
    echo ""
    echo "📱 Next steps:"
    echo "   1. Restart your backend service"
    echo "   2. Update mobile app"
    echo "   3. Test IMEI functionality"
else
    echo ""
    echo "❌ Migration failed!"
    echo "Please check the error messages above"
    exit 1
fi