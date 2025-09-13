#!/usr/bin/env python3
"""
Migration script to make magazine_id nullable in auto_sales and auto_loans tables.
This allows AUTO users (who don't belong to magazines) to create auto sales and loans.
"""

import os
import sys
import psycopg2
from sqlalchemy import create_engine, text

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def get_database_url():
    """Get database URL from environment or use default"""
    return os.getenv(
        'DATABASE_URL', 
        'postgresql://nasiya_user:23154216@localhost:5432/nasiya_bro'
    )

def run_migration():
    """Run the migration to make magazine_id nullable in auto tables"""
    try:
        engine = create_engine(get_database_url())
        
        with engine.connect() as conn:
            # Start a transaction
            trans = conn.begin()
            
            try:
                # Make magazine_id nullable in auto_sales table
                print("Making magazine_id nullable in auto_sales table...")
                conn.execute(text("""
                    ALTER TABLE auto_sales 
                    ALTER COLUMN magazine_id DROP NOT NULL;
                """))
                
                # Make magazine_id nullable in auto_loans table
                print("Making magazine_id nullable in auto_loans table...")
                conn.execute(text("""
                    ALTER TABLE auto_loans 
                    ALTER COLUMN magazine_id DROP NOT NULL;
                """))
                
                # Commit the transaction
                trans.commit()
                print("✅ Migration completed successfully!")
                print("   - auto_sales.magazine_id is now nullable")
                print("   - auto_loans.magazine_id is now nullable")
                
            except Exception as e:
                # Rollback on error
                trans.rollback()
                print(f"❌ Migration failed: {e}")
                raise
                
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("Running migration: make auto_sales and auto_loans magazine_id nullable")
    run_migration()