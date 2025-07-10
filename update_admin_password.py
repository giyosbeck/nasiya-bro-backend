#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal
from app.models.user import User, UserRole
from app.core.security import get_password_hash

def update_admin_password():
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.role == UserRole.ADMIN).first()
        if admin:
            new_password = "admin123"
            admin.password_hash = get_password_hash(new_password)
            db.commit()
            print(f"Updated admin password to: {new_password}")
            print(f"Admin phone: {admin.phone}")
        else:
            print("No admin found")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_admin_password()