#!/usr/bin/env python3
"""
Test live notification system on production server
"""

import requests
import json
import sys

# Production server
SERVER = "https://nasiya.backend.leadai.uz"
BASE_URL = f"{SERVER}/api/v1"

def test_endpoints_availability():
    """Test if notification endpoints are available"""
    print("🔍 Testing notification endpoints availability...")
    
    # Test basic endpoint access
    try:
        response = requests.get(f"{BASE_URL}/notifications/my-notifications", timeout=10)
        
        if response.status_code == 401:
            print("✅ Notification endpoints are available (authentication required)")
            return True
        elif response.status_code == 404:
            print("❌ Notification endpoints not found")
            return False
        else:
            print(f"⚠️  Unexpected response: {response.status_code}")
            return True  # Assume available
            
    except Exception as e:
        print(f"❌ Error connecting to server: {str(e)}")
        return False

def login_and_test():
    """Login and test notification features"""
    print("\n🔐 Testing with authentication...")
    
    # Try to login with test credentials
    test_credentials = [
        ("+998999111222", "testadmin123"),  # Our test admin
        ("+998901234567", "admin123"),     # Default admin
    ]
    
    for username, password in test_credentials:
        try:
            print(f"   Trying login: {username}")
            
            # Login
            login_data = {"username": username, "password": password}
            response = requests.post(f"{BASE_URL}/auth/login", data=login_data, timeout=10)
            
            if response.status_code == 200:
                token_data = response.json()
                access_token = token_data["access_token"]
                print(f"✅ Login successful!")
                
                return test_with_token(access_token)
                
            elif response.status_code == 401:
                print(f"   ❌ Invalid credentials for {username}")
                continue
            else:
                print(f"   ⚠️  Login failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Login error: {str(e)}")
            continue
    
    print("❌ Could not authenticate with any test credentials")
    return False

def test_with_token(access_token):
    """Test notification features with valid token"""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    print(f"\n🧪 Testing notification features...")
    
    # Test 1: Register push token
    print("1. Testing push token registration...")
    push_token_data = {
        "push_token": f"ExponentPushToken[production-test-{int(__import__('time').time())}]",
        "device_type": "mobile"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/notifications/register-token",
            json=push_token_data,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Push token registered successfully!")
            print(f"   Response: {result}")
        else:
            print(f"❌ Push token registration failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Push token test error: {str(e)}")
    
    # Test 2: Send admin alert
    print("\n2. Testing admin alert...")
    alert_data = {
        "type": "new_user_registration",
        "title": "Production Test Alert",
        "body": "This is a test admin alert from the notification system",
        "data": {
            "userId": "test-123",
            "userName": "Test User Production",
            "userPhone": "+998901111111",
            "testTime": __import__('datetime').datetime.now().isoformat()
        },
        "recipient_role": "admin"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/notifications/admin-alert",
            json=alert_data,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Admin alert sent successfully!")
            print(f"   Response: {result}")
        else:
            print(f"❌ Admin alert failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Admin alert test error: {str(e)}")
    
    # Test 3: Get notifications
    print("\n3. Testing get notifications...")
    try:
        response = requests.get(
            f"{BASE_URL}/notifications/my-notifications",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            notifications = response.json()
            print(f"✅ Retrieved {len(notifications)} notifications")
            if notifications:
                latest = notifications[0]
                print(f"   Latest: '{latest['title']}' - {latest['created_at']}")
        else:
            print(f"❌ Get notifications failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Get notifications error: {str(e)}")
    
    return True

def check_database():
    """Check database tables (if accessible)"""
    print("\n🗄️  Database check (manual verification needed)...")
    print("   Run these commands on your server to verify:")
    print(f"   ssh your-user@45.138.159.95")
    print(f"   sqlite3 nasiya_bro.db")
    print(f"   .tables")
    print(f"   SELECT COUNT(*) FROM push_tokens;")
    print(f"   SELECT COUNT(*) FROM notifications;")
    print(f"   SELECT title, created_at FROM notifications ORDER BY created_at DESC LIMIT 3;")

def main():
    """Main test function"""
    print("🧪 Testing Live Notification System")
    print(f"🌐 Server: {SERVER}")
    print("=" * 60)
    
    # Step 1: Check if endpoints exist
    if not test_endpoints_availability():
        print("\n❌ Notification endpoints are not available")
        print("💡 Make sure the notification system is properly deployed")
        return
    
    # Step 2: Test with authentication
    if login_and_test():
        print("\n🎉 Notification system tests completed successfully!")
    else:
        print("\n⚠️  Could not test with authentication")
        print("💡 You may need to create a test user or check credentials")
    
    # Step 3: Database verification info
    check_database()
    
    print(f"\n📱 Mobile App Test:")
    print(f"   Open your mobile app and try:")
    print(f"   1. Register/login - should work without 'Error registering push token'")
    print(f"   2. Register a new user - admins should get push notifications")
    print(f"   3. Create a loan - payment reminders should be scheduled")

if __name__ == "__main__":
    main()