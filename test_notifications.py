#!/usr/bin/env python3
"""
Test notification endpoints
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000/api/v1"

def test_notification_endpoints():
    """Test notification endpoints"""
    print("🧪 Testing Notification Endpoints...")
    
    # First, let's login to get a token (using test admin)
    login_data = {
        "username": "+998999111222",   # Test admin phone
        "password": "testadmin123"     # Test admin password
    }
    
    print("1. Logging in as admin...")
    try:
        response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data["access_token"]
            print(f"✅ Login successful! Token: {access_token[:20]}...")
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Login error: {str(e)}")
        return False
    
    # Headers with authentication
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # Test 2: Register push token
    print("\n2. Testing push token registration...")
    push_token_data = {
        "push_token": "ExponentPushToken[test-token-12345]",
        "device_type": "mobile"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/notifications/register-token",
            json=push_token_data,
            headers=headers
        )
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Push token registered: {result}")
        else:
            print(f"❌ Push token registration failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Push token error: {str(e)}")
    
    # Test 3: Send admin alert
    print("\n3. Testing admin alert...")
    alert_data = {
        "type": "new_user_registration",
        "title": "New User Registration",
        "body": "Test User has registered and needs approval",
        "data": {
            "userId": "test-123",
            "userName": "Test User",
            "userPhone": "+998901234567"
        },
        "recipient_role": "admin"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/notifications/admin-alert",
            json=alert_data,
            headers=headers
        )
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Admin alert sent: {result}")
        else:
            print(f"❌ Admin alert failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Admin alert error: {str(e)}")
    
    # Test 4: Get notifications
    print("\n4. Testing get notifications...")
    try:
        response = requests.get(
            f"{BASE_URL}/notifications/my-notifications",
            headers=headers
        )
        if response.status_code == 200:
            notifications = response.json()
            print(f"✅ Got {len(notifications)} notifications")
            if notifications:
                print(f"   Latest: {notifications[0]['title']}")
        else:
            print(f"❌ Get notifications failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Get notifications error: {str(e)}")
    
    # Test 5: Check database tables
    print("\n5. Checking database tables...")
    import sqlite3
    try:
        conn = sqlite3.connect("nasiya_bro.db")
        cursor = conn.cursor()
        
        # Check push tokens
        cursor.execute("SELECT COUNT(*) FROM push_tokens")
        token_count = cursor.fetchone()[0]
        print(f"✅ Push tokens in DB: {token_count}")
        
        # Check notifications 
        cursor.execute("SELECT COUNT(*) FROM notifications")
        notif_count = cursor.fetchone()[0]
        print(f"✅ Notifications in DB: {notif_count}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Database check error: {str(e)}")
    
    print("\n🎉 Notification system test completed!")
    return True

if __name__ == "__main__":
    test_notification_endpoints()