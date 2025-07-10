#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal, engine
from sqlalchemy import text

def check_database():
    with engine.connect() as connection:
        # Check magazines table structure
        result = connection.execute(text("PRAGMA table_info(magazines)"))
        columns = result.fetchall()
        print("Magazines table structure:")
        for col in columns:
            print(f"  {col}")
        
        print("\nMagazines data:")
        result = connection.execute(text("SELECT * FROM magazines"))
        magazines = result.fetchall()
        for mag in magazines:
            print(f"  {mag}")
        
        print("\nUsers with magazine info:")
        result = connection.execute(text("""
            SELECT id, name, phone, role, magazine_name, magazine_id, status 
            FROM users 
            WHERE role = 'manager' AND magazine_name IS NOT NULL
        """))
        users = result.fetchall()
        for user in users:
            print(f"  {user}")

if __name__ == "__main__":
    check_database()