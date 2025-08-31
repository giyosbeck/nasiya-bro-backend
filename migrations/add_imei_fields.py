#!/usr/bin/env python3
"""
PostgreSQL migration script to add IMEI fields to sales and loans tables.
Run this script after deploying the backend to add IMEI tracking functionality.
"""

import psycopg2
import os
from urllib.parse import urlparse

def get_db_connection():
    """Get PostgreSQL database connection from environment or default"""
    database_url = os.getenv('DATABASE_URL', 'postgresql://nasiya_user:nasiya_password@localhost:5432/nasiya_db')
    
    try:
        conn = psycopg2.connect(database_url)
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to database: {e}")
        return None

def add_imei_fields():
    """Add IMEI fields to sales and loans tables"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Add IMEI field to sales table
        print("Adding IMEI field to sales table...")
        cursor.execute("""
            ALTER TABLE sales 
            ADD COLUMN IF NOT EXISTS imei VARCHAR(20);
        """)
        
        # Add IMEI field to loans table  
        print("Adding IMEI field to loans table...")
        cursor.execute("""
            ALTER TABLE loans 
            ADD COLUMN IF NOT EXISTS imei VARCHAR(20);
        """)
        
        # Create index for IMEI searches
        print("Creating indexes for IMEI fields...")
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_sales_imei ON sales(imei);
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_loans_imei ON loans(imei);
        """)
        
        # Commit changes
        conn.commit()
        print("✅ Successfully added IMEI fields to database")
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Error adding IMEI fields: {e}")
        conn.rollback()
        return False
        
    finally:
        cursor.close()
        conn.close()

def rollback_imei_fields():
    """Rollback IMEI fields (for testing purposes)"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        print("Removing IMEI fields...")
        cursor.execute("ALTER TABLE sales DROP COLUMN IF EXISTS imei;")
        cursor.execute("ALTER TABLE loans DROP COLUMN IF EXISTS imei;")
        cursor.execute("DROP INDEX IF EXISTS idx_sales_imei;")
        cursor.execute("DROP INDEX IF EXISTS idx_loans_imei;")
        
        conn.commit()
        print("✅ Successfully removed IMEI fields")
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Error removing IMEI fields: {e}")
        conn.rollback()
        return False
        
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--rollback":
        rollback_imei_fields()
    else:
        add_imei_fields()