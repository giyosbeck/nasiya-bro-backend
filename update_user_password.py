#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash

def update_user_password():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.phone == "+998907654321").first()
        if user:
            new_password = "123456"
            user.password_hash = get_password_hash(new_password)
            db.commit()
            print(f"Updated password for user: {user.name}")
            print(f"Phone: {user.phone}")
            print(f"New password: {new_password}")
        else:
            print("User with phone 998907654321 not found")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_user_password()