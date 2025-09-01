#!/bin/bash
"""
Notification System Deployment Script
Upload and run this on your production server
"""

echo "🚀 Deploying Notification System to Production"
echo "=============================================="

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
    pip install httpx
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
echo "📦 Installing notification dependencies..."
pip install httpx

# Create database backup
echo "💾 Creating database backup..."
if [ -f "nasiya_bro.db" ]; then
    cp nasiya_bro.db "nasiya_bro_backup_$(date +%Y%m%d_%H%M%S).db"
    echo "✅ Database backed up"
else
    echo "⚠️  Database file not found - continuing without backup"
fi

# Run the notification database migration
echo "🗄️  Running notification database migration..."
python3 add_notification_tables.py

# Check if migration was successful
if [ $? -eq 0 ]; then
    echo "✅ Database migration completed successfully"
else
    echo "❌ Database migration failed!"
    exit 1
fi

# Test if the backend can start (dry run)
echo "🧪 Testing backend configuration..."
timeout 10 python3 -c "
import sys
sys.path.append('.')
try:
    from app.main import app
    from app.models.notification import PushToken, Notification, NotificationPreference
    from app.api.api_v1.endpoints.notifications import router
    print('✅ All notification imports successful')
except Exception as e:
    print(f'❌ Import error: {str(e)}')
    sys.exit(1)
"

# Check test result
if [ $? -eq 0 ]; then
    echo "✅ Backend configuration test passed"
else
    echo "❌ Backend configuration test failed!"
    echo "   Please check the error messages above"
    exit 1
fi

# Success message
echo ""
echo "🎉 Notification System Deployed Successfully!"
echo "✅ Database tables created"
echo "✅ API endpoints added"
echo "✅ Dependencies installed"
echo "✅ Configuration validated"
echo ""
echo "📱 New API Endpoints Available:"
echo "   POST /api/v1/notifications/register-token"
echo "   POST /api/v1/notifications/admin-alert"  
echo "   GET  /api/v1/notifications/my-notifications"
echo "   POST /api/v1/notifications/preferences"
echo ""
echo "🔄 Next steps:"
echo "   1. Restart your backend service (pm2 restart / systemctl restart / etc.)"
echo "   2. Test endpoints with curl or mobile app"
echo "   3. Check backend logs for any startup errors"
echo ""
echo "🧪 Quick test command:"
echo "   curl https://nasiya.backend.leadai.uz/api/v1/notifications/my-notifications"