#!/usr/bin/env python3
"""
Deploy notification system to production server
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def run_command(command, description=""):
    """Run shell command and return result"""
    print(f"🔄 {description}...")
    print(f"   Command: {command}")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            print(f"✅ {description} successful")
            if result.stdout:
                print(f"   Output: {result.stdout.strip()}")
            return True, result.stdout
        else:
            print(f"❌ {description} failed")
            print(f"   Error: {result.stderr}")
            return False, result.stderr
            
    except subprocess.TimeoutExpired:
        print(f"❌ {description} timed out")
        return False, "Timeout"
    except Exception as e:
        print(f"❌ {description} error: {str(e)}")
        return False, str(e)

def create_deployment_package():
    """Create deployment package with notification files"""
    print("📦 Creating deployment package...")
    
    # Files to deploy
    notification_files = [
        "app/models/notification.py",
        "app/api/api_v1/endpoints/notifications.py", 
        "app/schemas/notification.py",
        "app/services/notification_service.py",
        "add_notification_tables.py",
        "requirements.txt"
    ]
    
    # Modified files
    modified_files = [
        "app/models/__init__.py",
        "app/api/api_v1/api.py"
    ]
    
    # Create deployment directory
    deploy_dir = Path("deploy_notifications")
    deploy_dir.mkdir(exist_ok=True)
    
    # Copy files maintaining structure
    for file_path in notification_files + modified_files:
        src = Path(file_path)
        if src.exists():
            dst = deploy_dir / file_path
            dst.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file
            with open(src, 'r') as f:
                content = f.read()
            with open(dst, 'w') as f:
                f.write(content)
            
            print(f"✅ Copied: {file_path}")
        else:
            print(f"⚠️  Missing: {file_path}")
    
    # Create deployment script
    deploy_script = deploy_dir / "deploy.sh"
    with open(deploy_script, 'w') as f:
        f.write("""#!/bin/bash

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
""")
    
    deploy_script.chmod(0o755)
    
    # Create deployment README
    readme = deploy_dir / "README.md"
    with open(readme, 'w') as f:
        f.write("""# Notification System Deployment

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
""")
    
    print(f"📦 Deployment package created in: {deploy_dir}")
    return deploy_dir

def test_production_endpoints():
    """Test production server endpoints"""
    print("🧪 Testing production endpoints...")
    
    # Try to access the production API
    servers = [
        "https://nasiya.backend.leadai.uz",
        "http://45.138.159.95"
    ]
    
    for server in servers:
        print(f"\n🌐 Testing server: {server}")
        
        # Test basic endpoint
        success, output = run_command(
            f'curl -s -w "\\nHTTP_CODE:%{{http_code}}" {server}/api/v1/auth/login -X POST -H "Content-Type: application/x-www-form-urlencoded" -d "username=test&password=test" --connect-timeout 10',
            f"Test {server} connection"
        )
        
        if "HTTP_CODE:422" in output or "HTTP_CODE:401" in output:
            print(f"✅ {server} is accessible (auth working)")
            return server
        elif "HTTP_CODE:200" in output:
            print(f"✅ {server} is accessible")
            return server
        else:
            print(f"❌ {server} not accessible or down")
    
    return None

def main():
    """Main deployment function"""
    print("🚀 Starting Notification System Deployment Preparation...")
    
    # Check if we're in the right directory
    if not os.path.exists("app/main.py"):
        print("❌ Please run this script from the backend directory")
        sys.exit(1)
    
    # Test production server
    production_server = test_production_endpoints()
    if not production_server:
        print("❌ Cannot connect to production server")
        print("💡 Make sure the server is running and accessible")
    
    # Create deployment package
    deploy_dir = create_deployment_package()
    
    print(f"""
🎉 Deployment preparation completed!

📋 Next Steps:

1. **Upload to server:**
   scp -r {deploy_dir}/* user@your-server:/path/to/backend/

2. **SSH to server and run:**
   cd /path/to/backend
   chmod +x deploy.sh
   ./deploy.sh

3. **Restart backend service on server**

4. **Test endpoints:**
   curl {production_server or 'https://nasiya.backend.leadai.uz'}/api/v1/notifications/my-notifications

📁 Files ready in: {deploy_dir.absolute()}
""")

if __name__ == "__main__":
    main()