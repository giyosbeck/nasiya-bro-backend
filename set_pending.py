#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal
from app.models.user import User, UserRole, UserStatus

def set_all_users_pending():
    db = SessionLocal()
    try:
        # Set all non-admin users to pending
        non_admin_users = db.query(User).filter(User.role != UserRole.ADMIN).all()
        for user in non_admin_users:
            user.status = UserStatus.PENDING
            print(f'Set {user.name} ({user.phone}) to pending')
        db.commit()
        print(f'Updated {len(non_admin_users)} users to pending status')
    except Exception as e:
        print(f'Error: {e}')
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    set_all_users_pending()