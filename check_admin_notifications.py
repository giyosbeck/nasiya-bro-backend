#!/usr/bin/env python3
"""
Check admin notification setup and test functionality
"""

import sqlite3
import sys
import os
from datetime import datetime

def check_admin_notification_setup():
    """Check if admin notification system is properly set up"""
    print("🔍 Checking admin notification setup...")
    
    try:
        # Connect to database
        conn = sqlite3.connect("nasiya_bro.db")
        cursor = conn.cursor()
        
        # Check 1: Do notification tables exist?
        print("\n1. Checking notification tables...")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('push_tokens', 'notifications', 'notification_preferences')")
        tables = cursor.fetchall()
        table_names = [table[0] for table in tables]
        
        required_tables = ['push_tokens', 'notifications', 'notification_preferences']
        for table in required_tables:
            if table in table_names:
                print(f"   ✅ {table} table exists")
            else:
                print(f"   ❌ {table} table missing")
        
        if len(table_names) != len(required_tables):
            print("   💡 Run: python3 add_notification_tables.py")
            return False
        
        # Check 2: Do admin users exist?
        print("\n2. Checking admin users...")
        cursor.execute("SELECT id, name, phone, role FROM users WHERE role = 'admin' OR role = 'ADMIN'")
        admins = cursor.fetchall()
        
        if not admins:
            print("   ❌ No admin users found")
            print("   💡 Create an admin user first")
            return False
        
        print(f"   ✅ Found {len(admins)} admin user(s):")
        for admin in admins:
            print(f"      • ID {admin[0]}: {admin[1]} ({admin[2]})")
        
        # Check 3: Do admins have push tokens registered?
        print("\n3. Checking admin push tokens...")
        admin_ids = [str(admin[0]) for admin in admins]
        
        if admin_ids:
            placeholders = ','.join(['?'] * len(admin_ids))
            cursor.execute(f"SELECT user_id, token, is_active, created_at FROM push_tokens WHERE user_id IN ({placeholders})", admin_ids)
            tokens = cursor.fetchall()
            
            if not tokens:
                print("   ❌ No push tokens registered for admin users")
                print("   💡 Admins need to login to mobile app to register push tokens")
                return False
            
            print(f"   ✅ Found {len(tokens)} push token(s) for admin users:")
            for token in tokens:
                status = "Active" if token[2] else "Inactive"
                print(f"      • User {token[0]}: {status} (registered: {token[3]})")
        
        # Check 4: Recent notifications
        print("\n4. Checking recent notifications...")
        cursor.execute("SELECT type, title, recipient_user_id, status, created_at FROM notifications ORDER BY created_at DESC LIMIT 5")
        notifications = cursor.fetchall()
        
        if not notifications:
            print("   ℹ️  No notifications in database yet")
        else:
            print(f"   📬 Found {len(notifications)} recent notification(s):")
            for notif in notifications:
                print(f"      • {notif[1]} ({notif[0]}) → User {notif[2]} [{notif[3]}] at {notif[4]}")
        
        cursor.close()
        conn.close()
        
        # Summary
        print(f"\n📊 Summary:")
        print(f"   • Tables: ✅ All required tables exist")
        print(f"   • Admin users: ✅ {len(admins)} admin(s) found")
        print(f"   • Push tokens: {'✅' if tokens else '❌'} {len(tokens) if tokens else 0} token(s)")
        print(f"   • Recent notifications: {len(notifications)} in database")
        
        if tokens:
            print(f"\n🎯 Next steps to test:")
            print(f"   1. Register a new user from mobile app")
            print(f"   2. Check backend logs: sudo journalctl -u nasiya-bro --since '1 minute ago'")
            print(f"   3. Check if admins receive push notifications")
            return True
        else:
            print(f"\n⚠️  Issue found:")
            print(f"   • Admin users exist but have no push tokens registered")
            print(f"   • Admins need to login to mobile app to register their devices")
            print(f"   • After admin login, try registering a new user")
            return False
            
    except Exception as e:
        print(f"❌ Error checking setup: {str(e)}")
        return False

def create_test_notification():
    """Create a test notification to verify system works"""
    print("\n🧪 Creating test notification...")
    
    try:
        conn = sqlite3.connect("nasiya_bro.db")
        cursor = conn.cursor()
        
        # Get first admin with push token
        cursor.execute("""
            SELECT u.id, u.name, pt.id, pt.token 
            FROM users u 
            JOIN push_tokens pt ON u.id = pt.user_id 
            WHERE u.role IN ('admin', 'ADMIN') AND pt.is_active = 1 
            LIMIT 1
        """)
        
        result = cursor.fetchone()
        if not result:
            print("   ❌ No admin with active push token found")
            return False
        
        admin_id, admin_name, token_id, push_token = result
        
        # Create test notification
        cursor.execute("""
            INSERT INTO notifications 
            (type, title, body, data, recipient_user_id, push_token_id, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            'new_user_registration',
            'Test Admin Notification',
            'This is a test notification to verify the admin alert system is working',
            '{"test": true, "userId": "test-123", "userName": "Test User"}',
            admin_id,
            token_id,
            'pending',
            datetime.now().isoformat()
        ))
        
        conn.commit()
        notification_id = cursor.lastrowid
        
        print(f"   ✅ Test notification created (ID: {notification_id})")
        print(f"   📱 Recipient: {admin_name} (User ID: {admin_id})")
        print(f"   📋 Push token: {push_token[:30]}...")
        
        cursor.close()
        conn.close()
        
        print(f"\n💡 To send this notification:")
        print(f"   python3 -c \"")
        print(f"import asyncio")
        print(f"from app.services.notification_service import NotificationService")
        print(f"asyncio.run(NotificationService().send_push_notification(")
        print(f"    '{push_token}',")
        print(f"    'Test Admin Notification',")
        print(f"    'This is a test notification',")
        print(f"    {{'test': True}},")
        print(f"    {notification_id}")
        print(f"))")
        print(f"\"")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error creating test notification: {str(e)}")
        return False

def main():
    """Main function"""
    print("🚀 Admin Notification Diagnostic Tool")
    print("=" * 50)
    
    # Check if database exists
    if not os.path.exists("nasiya_bro.db"):
        print("❌ Database file not found!")
        print("   Make sure you're running this from the backend directory")
        sys.exit(1)
    
    # Check setup
    setup_ok = check_admin_notification_setup()
    
    if setup_ok:
        print(f"\n🎉 Admin notification system appears to be set up correctly!")
        
        # Offer to create test notification
        create_test = input("\n❓ Create a test notification? (y/n): ").lower().strip()
        if create_test == 'y':
            create_test_notification()
    else:
        print(f"\n❌ Admin notification system needs attention")
        print(f"   Follow the suggestions above to fix the issues")

if __name__ == "__main__":
    main()