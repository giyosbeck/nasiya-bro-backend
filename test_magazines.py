#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal
from app.models.magazine import Magazine, MagazineStatus
from app.models.user import User

def test_magazines():
    db = SessionLocal()
    try:
        # Check existing magazines
        magazines = db.query(Magazine).all()
        print(f"Existing magazines: {len(magazines)}")
        
        for mag in magazines:
            print(f"- {mag.name}: {mag.status.value if mag.status else 'None'}")
        
        # Check users with magazine_name but no magazine relationship
        users_with_magazine_name = db.query(User).filter(
            User.magazine_name.isnot(None),
            User.role == 'manager'
        ).all()
        
        print(f"\nUsers with magazine_name: {len(users_with_magazine_name)}")
        
        # Create magazines for users who don't have them
        for user in users_with_magazine_name:
            # Check if magazine already exists
            existing_mag = db.query(Magazine).filter(Magazine.name == user.magazine_name).first()
            if not existing_mag:
                print(f"Creating magazine: {user.magazine_name}")
                new_magazine = Magazine(
                    name=user.magazine_name,
                    status=MagazineStatus.PENDING,
                    phone=user.phone
                )
                db.add(new_magazine)
                db.flush()  # Get the ID
                
                # Update user's magazine_id
                user.magazine_id = new_magazine.id
            else:
                # Update user's magazine_id if not set
                if not user.magazine_id:
                    user.magazine_id = existing_mag.id
                    print(f"Linked user {user.name} to existing magazine {existing_mag.name}")
        
        db.commit()
        
        # Show final state
        magazines = db.query(Magazine).all()
        print(f"\nFinal magazines: {len(magazines)}")
        for mag in magazines:
            print(f"- {mag.name}: {mag.status.value if mag.status else 'None'}")
            
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    test_magazines()