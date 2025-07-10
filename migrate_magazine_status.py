#!/usr/bin/env python3
"""
Migration script to add status and subscription fields to magazines table.
"""
import sys
import os
from datetime import date, timedelta

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal, engine
from sqlalchemy import text

def migrate_magazine_table():
    """Add status and subscription fields to magazines table."""
    print("Starting magazine table migration...")
    
    with engine.connect() as connection:
        try:
            # Check if columns already exist
            result = connection.execute(text("PRAGMA table_info(magazines)"))
            columns = [row[1] for row in result.fetchall()]
            
            print(f"Current columns: {columns}")
            
            # Add status column if it doesn't exist
            if 'status' not in columns:
                print("Adding status column...")
                connection.execute(text("""
                    ALTER TABLE magazines 
                    ADD COLUMN status TEXT DEFAULT 'pending'
                """))
                print("✅ Status column added")
            else:
                print("✅ Status column already exists")
            
            # Add subscription_end_date column if it doesn't exist
            if 'subscription_end_date' not in columns:
                print("Adding subscription_end_date column...")
                connection.execute(text("""
                    ALTER TABLE magazines 
                    ADD COLUMN subscription_end_date DATE
                """))
                print("✅ Subscription end date column added")
            else:
                print("✅ Subscription end date column already exists")
            
            # Add approved_by column if it doesn't exist
            if 'approved_by' not in columns:
                print("Adding approved_by column...")
                connection.execute(text("""
                    ALTER TABLE magazines 
                    ADD COLUMN approved_by INTEGER
                """))
                print("✅ Approved by column added")
            else:
                print("✅ Approved by column already exists")
            
            # Commit the changes
            connection.commit()
            
            print("✅ Magazine table migration completed successfully!")
            
        except Exception as e:
            print(f"❌ Error during migration: {str(e)}")
            connection.rollback()
            raise

def update_existing_magazines():
    """Update existing magazines with default status."""
    print("Updating existing magazines...")
    
    db = SessionLocal()
    try:
        # Update all existing magazines to have pending status
        result = db.execute(text("""
            UPDATE magazines 
            SET status = 'pending' 
            WHERE status IS NULL OR status = ''
        """))
        
        db.commit()
        print(f"✅ Updated {result.rowcount} magazines to pending status")
        
    except Exception as e:
        print(f"❌ Error updating magazines: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    migrate_magazine_table()
    update_existing_magazines()
    print("\n🎉 Migration completed! Magazine table now has status and subscription fields.")