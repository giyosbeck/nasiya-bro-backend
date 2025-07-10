#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal, engine
from sqlalchemy import text

def fix_magazine_status():
    """Fix magazine status values to match enum."""
    print("Fixing magazine status values...")
    
    with engine.connect() as connection:
        try:
            # Update lowercase status values to uppercase
            connection.execute(text("""
                UPDATE magazines 
                SET status = 'PENDING' 
                WHERE status = 'pending'
            """))
            
            connection.execute(text("""
                UPDATE magazines 
                SET status = 'ACTIVE' 
                WHERE status = 'active'
            """))
            
            connection.execute(text("""
                UPDATE magazines 
                SET status = 'INACTIVE' 
                WHERE status = 'inactive'
            """))
            
            connection.commit()
            
            # Check the results
            result = connection.execute(text("SELECT name, status FROM magazines"))
            magazines = result.fetchall()
            
            print("Updated magazines:")
            for mag in magazines:
                print(f"  {mag[0]}: {mag[1]}")
                
            print("✅ Magazine status values fixed!")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            connection.rollback()

if __name__ == "__main__":
    fix_magazine_status()