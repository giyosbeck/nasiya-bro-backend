#!/usr/bin/env python3
"""
PostgreSQL migration script to add IMEI fields to sales and loans tables.
Run this script on your deployed server to add IMEI tracking functionality.
"""

import psycopg2
import os
import sys
from urllib.parse import urlparse

def get_db_connection():
    """Get PostgreSQL database connection"""
    # Try environment variable first
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL environment variable not found")
        print("\nPlease set DATABASE_URL or provide connection details:")
        print("Example: DATABASE_URL=postgresql://user:password@host:port/database")
        print("\nOr run with connection string:")
        print("DATABASE_URL='postgresql://user:pass@host:port/db' python migrations/add_imei_fields.py")
        return None
    
    try:
        print(f"🔗 Connecting to database...")
        # Parse URL to hide password in logs
        parsed = urlparse(database_url)
        safe_url = f"postgresql://{parsed.username}:***@{parsed.hostname}:{parsed.port}{parsed.path}"
        print(f"   Database: {safe_url}")
        
        conn = psycopg2.connect(database_url)
        print("✅ Database connection successful")
        return conn
    except psycopg2.Error as e:
        print(f"❌ Error connecting to database: {e}")
        print("\nTroubleshooting:")
        print("1. Check if PostgreSQL server is running")
        print("2. Verify database credentials")
        print("3. Ensure database exists")
        print("4. Check network connectivity to database server")
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