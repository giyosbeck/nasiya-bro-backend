#!/usr/bin/env python3
"""
Migration script to change default value of count column in auto_products table from 0 to 1.
This ensures new auto products start with 1 unit by default.
"""

import os
import sys
from sqlalchemy import create_engine, text

def get_database_url():
    """Get database URL from environment or use default"""
    return os.getenv(
        'DATABASE_URL', 
        'postgresql://nasiya_user:23154216@localhost:5432/nasiya_bro'
    )

def run_migration():
    """Run the migration to change default count value"""
    try:
        engine = create_engine(get_database_url())
        
        with engine.connect() as conn:
            trans = conn.begin()
            
            try:
                # Change the default value of count column to 1
                print("Changing default value of auto_products.count from 0 to 1...")
                conn.execute(text("""
                    ALTER TABLE auto_products 
                    ALTER COLUMN count SET DEFAULT 1;
                """))
                
                # Update existing records with count=0 to count=1 (newly created products)
                print("Updating recently created products with count=0 to count=1...")
                result = conn.execute(text("""
                    UPDATE auto_products 
                    SET count = 1 
                    WHERE count = 0 
                    AND created_at >= CURRENT_DATE;
                """))
                
                updated_rows = result.rowcount
                print(f"Updated {updated_rows} recently created products")
                
                trans.commit()
                print("✅ Migration completed successfully!")
                print("   - Default count value changed to 1")
                print(f"   - {updated_rows} existing products updated")
                
            except Exception as e:
                trans.rollback()
                print(f"❌ Migration failed: {e}")
                raise
                
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("Running migration: fix auto_products default count")
    run_migration()