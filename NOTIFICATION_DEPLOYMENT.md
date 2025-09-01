# 🚀 Notification System Production Deployment

## 📋 Overview
Deploy the complete notification system (local + push notifications) to your production server.

## 🎯 What This Adds
- **Database Tables**: `push_tokens`, `notifications`, `notification_preferences`
- **API Endpoints**: 4 new notification endpoints
- **Push Notifications**: Expo push notification integration
- **Admin Alerts**: New user registration notifications
- **Mobile Integration**: Fixes "Error registering push token" error

## 📦 Quick Deployment (Recommended)

### Option 1: Direct Upload & Run
```bash
# 1. Upload files to server
scp deploy_notification_system.sh user@your-server:/path/to/backend/
scp add_notification_tables.py user@your-server:/path/to/backend/
scp -r app/models/notification.py user@your-server:/path/to/backend/app/models/
scp -r app/api/api_v1/endpoints/notifications.py user@your-server:/path/to/backend/app/api/api_v1/endpoints/
scp -r app/schemas/notification.py user@your-server:/path/to/backend/app/schemas/
scp -r app/services/notification_service.py user@your-server:/path/to/backend/app/services/
scp app/models/__init__.py user@your-server:/path/to/backend/app/models/
scp app/api/api_v1/api.py user@your-server:/path/to/backend/app/api/api_v1/

# 2. SSH to server and run
ssh user@your-server
cd /path/to/backend
chmod +x deploy_notification_system.sh
./deploy_notification_system.sh

# 3. Restart your backend service
pm2 restart nasiya-backend  # or whatever your service name is
# OR
systemctl restart your-backend-service
# OR 
pkill -f "python.*run.py" && nohup python3 run.py > backend.log 2>&1 &
```

### Option 2: Use Prepared Package
```bash
# 1. Upload the entire deploy package
scp -r deploy_notifications/* user@your-server:/path/to/backend/

# 2. SSH and run the deployment
ssh user@your-server
cd /path/to/backend  
chmod +x deploy.sh
./deploy.sh

# 3. Restart backend service
```

## 🧪 Testing After Deployment

```bash
# Test 1: Check if endpoints are available
curl https://nasiya.backend.leadai.uz/api/v1/notifications/my-notifications

# Should return: {"detail":"Not authenticated"} (means endpoint exists)

# Test 2: Check database tables
sqlite3 nasiya_bro.db "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%notification%' OR name='push_tokens';"

# Should show: push_tokens, notifications, notification_preferences
```

## 🔧 Troubleshooting

### Common Issues:

1. **"Module not found" error**:
   ```bash
   pip install httpx
   ```

2. **"Permission denied" on database**:
   ```bash
   chmod 664 nasiya_bro.db
   chown www-data:www-data nasiya_bro.db  # adjust user as needed
   ```

3. **Backend won't start**:
   ```bash
   python3 -c "from app.main import app; print('✅ Import successful')"
   ```

4. **Mobile app still shows error**:
   - Make sure backend service is restarted
   - Check backend logs for errors
   - Verify mobile app is pointing to correct server URL

## 📱 Mobile App Integration

After deployment, the mobile app will automatically:
- ✅ Register push tokens successfully (no more errors)
- ✅ Send admin alerts when new users register  
- ✅ Continue working with local payment notifications

## 🎉 Success Indicators

1. **Backend logs show**: `INFO: Application startup complete.`
2. **Curl test returns**: `{"detail":"Not authenticated"}`
3. **Database has new tables**: `push_tokens`, `notifications`, `notification_preferences`
4. **Mobile app**: No more "Error registering push token" messages

## 📊 Production Endpoints

- `POST /api/v1/notifications/register-token` - Mobile app registers push tokens
- `POST /api/v1/notifications/admin-alert` - Send admin alerts  
- `GET /api/v1/notifications/my-notifications` - Get user notifications
- `POST /api/v1/notifications/preferences` - Manage notification settings

## 🔄 Rollback Plan

If something goes wrong:
```bash
# Stop backend
pkill -f "python.*run.py"

# Restore database
cp nasiya_bro_backup_YYYYMMDD_HHMMSS.db nasiya_bro.db

# Remove notification files (optional)
rm -f app/models/notification.py app/schemas/notification.py
rm -f app/api/api_v1/endpoints/notifications.py app/services/notification_service.py

# Restart with old code
python3 run.py
```