#!/usr/bin/env python3
"""
Test production notification endpoints
"""

import requests
import json
import sys

# Production servers to test
SERVERS = [
    "https://nasiya.backend.leadai.uz",
    "http://45.138.159.95"
]

def test_server_endpoints(base_url):
    """Test notification endpoints on a server"""
    print(f"🌐 Testing server: {base_url}")
    
    try:
        # Test 1: Basic connectivity
        response = requests.get(f"{base_url}/api/v1", timeout=10)
        if response.status_code not in [200, 404, 422]:
            print(f"❌ Server not accessible: {response.status_code}")
            return False
        
        print("✅ Server is accessible")
        
        # Test 2: Check if notification endpoints exist
        response = requests.get(f"{base_url}/api/v1/notifications/my-notifications", timeout=10)
        
        if response.status_code == 401:
            print("✅ Notification endpoints exist (authentication required)")
            return True
        elif response.status_code == 404:
            print("❌ Notification endpoints not found (not deployed yet)")
            return False
        else:
            print(f"⚠️  Unexpected response: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectTimeout:
        print(f"❌ Connection timeout to {base_url}")
        return False
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection error to {base_url}")
        return False
    except Exception as e:
        print(f"❌ Error testing {base_url}: {str(e)}")
        return False

def test_with_auth(base_url):
    """Test with authentication if possible"""
    print(f"\n🔐 Testing authenticated endpoints on {base_url}")
    
    # Common test credentials (adjust as needed)
    test_credentials = [
        ("+998999111222", "testadmin123"),  # Our test admin
        ("+998901234567", "admin123"),     # Common admin
    ]
    
    for username, password in test_credentials:
        try:
            # Try to login
            login_data = {"username": username, "password": password}
            response = requests.post(
                f"{base_url}/api/v1/auth/login", 
                data=login_data, 
                timeout=10
            )
            
            if response.status_code == 200:
                token_data = response.json()
                access_token = token_data["access_token"]
                print(f"✅ Login successful with {username}")
                
                # Test notification endpoints with token
                headers = {"Authorization": f"Bearer {access_token}"}
                
                # Test register token
                token_data = {
                    "push_token": "ExponentPushToken[production-test]",
                    "device_type": "mobile"
                }
                response = requests.post(
                    f"{base_url}/api/v1/notifications/register-token",
                    json=token_data,
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    print("✅ Push token registration working")
                else:
                    print(f"⚠️  Push token registration: {response.status_code}")
                
                # Test get notifications
                response = requests.get(
                    f"{base_url}/api/v1/notifications/my-notifications",
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    notifications = response.json()
                    print(f"✅ Get notifications working ({len(notifications)} notifications)")
                else:
                    print(f"⚠️  Get notifications: {response.status_code}")
                
                return True
                
            elif response.status_code == 401:
                continue  # Try next credentials
            else:
                print(f"⚠️  Login attempt failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Auth test error: {str(e)}")
            continue
    
    print("⚠️  Could not authenticate with test credentials")
    return False

def main():
    """Main test function"""
    print("🧪 Testing Production Notification System")
    print("=" * 50)
    
    working_servers = []
    
    # Test each server
    for server in SERVERS:
        if test_server_endpoints(server):
            working_servers.append(server)
            
        print("-" * 30)
    
    # Summary
    print(f"\n📊 Test Results:")
    print(f"✅ Working servers: {len(working_servers)}")
    print(f"❌ Failed servers: {len(SERVERS) - len(working_servers)}")
    
    if working_servers:
        print(f"\n🎉 Notification system is deployed on:")
        for server in working_servers:
            print(f"   • {server}")
            
        # Try authenticated tests on first working server
        if working_servers:
            test_with_auth(working_servers[0])
    else:
        print(f"\n❌ Notification system is not deployed on any server")
        print(f"💡 Please run the deployment script first")
    
    print(f"\n📋 Manual test commands:")
    for server in working_servers:
        print(f"curl {server}/api/v1/notifications/my-notifications")

if __name__ == "__main__":
    main()