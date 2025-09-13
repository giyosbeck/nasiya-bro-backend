#!/usr/bin/env python3
"""
Migration script to make magazine_id nullable in auto_products table.
This allows AUTO users (who don't belong to magazines) to create auto products.
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
    """Run the migration to make magazine_id nullable in auto_products"""
    try:
        engine = create_engine(get_database_url())
        
        with engine.connect() as conn:
            # Start a transaction
            trans = conn.begin()
            
            try:
                # Drop the NOT NULL constraint on magazine_id
                print("Making magazine_id nullable in auto_products table...")
                conn.execute(text("""
                    ALTER TABLE auto_products 
                    ALTER COLUMN magazine_id DROP NOT NULL;
                """))
                
                # Commit the transaction
                trans.commit()
                print("✅ Migration completed successfully!")
                
            except Exception as e:
                # Rollback on error
                trans.rollback()
                print(f"❌ Migration failed: {e}")
                raise
                
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("Running migration: make auto_products.magazine_id nullable")
    run_migration()