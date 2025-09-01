#!/usr/bin/env python3
"""
Create a test admin user for notification testing
"""

import sqlite3
import sys
import os
from passlib.context import CryptContext

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def create_test_admin():
    """Create a test admin user"""
    
    # Password hashing setup
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    # Test admin credentials
    phone = "+998999111222"
    password = "testadmin123"
    name = "Test Admin for Notifications"
    hashed_password = pwd_context.hash(password)
    
    try:
        # Connect to database
        conn = sqlite3.connect("nasiya_bro.db")
        cursor = conn.cursor()
        
        # Check if user already exists
        cursor.execute("SELECT id FROM users WHERE phone = ?", (phone,))
        if cursor.fetchone():
            print(f"✅ Test admin already exists: {phone}")
            cursor.close()
            conn.close()
            return phone, password
        
        # Insert test admin user
        cursor.execute("""
            INSERT INTO users (name, phone, password_hash, role, status, created_at)
            VALUES (?, ?, ?, 'ADMIN', 'ACTIVE', datetime('now'))
        """, (name, phone, hashed_password))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"✅ Created test admin user:")
        print(f"   Phone: {phone}")
        print(f"   Password: {password}")
        
        return phone, password
        
    except Exception as e:
        print(f"❌ Error creating test admin: {str(e)}")
        return None, None

if __name__ == "__main__":
    phone, password = create_test_admin()
    if phone and password:
        print(f"\n🎯 Use these credentials for testing:")
        print(f"   Username: {phone}")
        print(f"   Password: {password}")