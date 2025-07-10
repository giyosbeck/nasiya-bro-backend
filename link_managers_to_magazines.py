#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal
from app.models.magazine import Magazine
from app.models.user import User, UserRole

def link_managers_to_magazines():
    """Link managers to their magazines based on magazine_name."""
    db = SessionLocal()
    try:
        # Get all magazines
        magazines = db.query(Magazine).all()
        print(f"Found {len(magazines)} magazines")
        
        # Get all managers
        managers = db.query(User).filter(
            User.role == UserRole.MANAGER,
            User.magazine_name.isnot(None)
        ).all()
        print(f"Found {len(managers)} managers with magazine names")
        
        for manager in managers:
            # Find matching magazine by name
            magazine = db.query(Magazine).filter(
                Magazine.name == manager.magazine_name
            ).first()
            
            if magazine:
                # Link manager to magazine
                manager.magazine_id = magazine.id
                print(f"Linked {manager.name} to magazine {magazine.name}")
            else:
                print(f"No magazine found for {manager.name} (magazine: {manager.magazine_name})")
        
        db.commit()
        
        # Show results
        print("\nFinal linking status:")
        for magazine in magazines:
            linked_managers = db.query(User).filter(
                User.magazine_id == magazine.id,
                User.role == UserRole.MANAGER
            ).all()
            
            manager_names = [m.name for m in linked_managers]
            print(f"Magazine '{magazine.name}': {len(linked_managers)} managers - {manager_names}")
            
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    link_managers_to_magazines()