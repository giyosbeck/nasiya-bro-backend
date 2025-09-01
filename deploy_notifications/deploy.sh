#!/bin/bash

# Notification System Deployment Script
echo "🚀 Deploying Notification System..."

# Backup database
echo "💾 Creating database backup..."
cp nasiya_bro.db "nasiya_bro_backup_$(date +%Y%m%d_%H%M%S).db"

# Install dependencies
echo "📦 Installing dependencies..."
pip install httpx

# Run database migration
echo "🗄️  Running database migration..."
python3 add_notification_tables.py

# Copy new files
echo "📁 Copying notification files..."
cp -r app/* ./app/ 2>/dev/null || true

# Restart backend service (adjust command as needed)
echo "🔄 Restarting backend service..."
# pkill -f "python.*run.py" 2>/dev/null || true
# nohup python3 run.py > backend.log 2>&1 &

echo "✅ Notification system deployment completed!"
echo "📋 Next steps:"
echo "   1. Restart your backend process"
echo "   2. Test endpoints: /api/v1/notifications/"
echo "   3. Check logs for any errors"
