# Notification System Deployment

## Files Included:
- Database migration script: `add_notification_tables.py`
- New models: `app/models/notification.py`
- New endpoints: `app/api/api_v1/endpoints/notifications.py` 
- New schemas: `app/schemas/notification.py`
- New service: `app/services/notification_service.py`
- Updated files: `app/models/__init__.py`, `app/api/api_v1/api.py`

## Deployment Steps:

1. **Upload files to server:**
   ```bash
   scp -r deploy_notifications/* user@server:/path/to/backend/
   ```

2. **Run deployment script:**
   ```bash
   chmod +x deploy.sh
   ./deploy.sh
   ```

3. **Restart backend service**

4. **Test endpoints:**
   ```bash
   curl http://your-server/api/v1/notifications/my-notifications
   ```

## New Endpoints:
- `POST /api/v1/notifications/register-token`
- `POST /api/v1/notifications/admin-alert`  
- `GET /api/v1/notifications/my-notifications`
- `POST /api/v1/notifications/preferences`

## Database Tables Created:
- `push_tokens` - Device push tokens
- `notifications` - Notification records
- `notification_preferences` - User preferences
