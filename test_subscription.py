#!/usr/bin/env python3
"""
Test script for subscription functionality.
This script tests the new subscription features.
"""
import sys
import os
from datetime import date, timedelta

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal
from app.models.user import User, UserRole, UserStatus
from app.services.subscription_service import check_and_deactivate_expired_users, get_users_expiring_soon

def test_subscription_functionality():
    """Test the subscription functionality."""
    print("Testing subscription functionality...")
    
    db = SessionLocal()
    
    try:
        # Get all users
        users = db.query(User).all()
        print(f"Total users in database: {len(users)}")
        
        # Show user subscription status
        for user in users:
            print(f"User: {user.name} ({user.phone})")
            print(f"  Role: {user.role.value}")
            print(f"  Status: {user.status.value}")
            print(f"  Subscription end date: {user.subscription_end_date}")
            print()
        
        # Test expired user checking
        print("Testing expired user checking...")
        result = check_and_deactivate_expired_users()
        print(f"Expired user check result: {result}")
        print()
        
        # Test expiring soon functionality
        print("Testing expiring soon functionality...")
        expiring_result = get_users_expiring_soon(30)  # Check next 30 days
        print(f"Expiring soon result: {expiring_result}")
        print()
        
        print("Subscription functionality test completed!")
        
    except Exception as e:
        print(f"Error during test: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    test_subscription_functionality()