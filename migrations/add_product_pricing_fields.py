"""
Migration to add purchase_price and sale_price to products table
Run this script to update the database schema
"""

import sqlite3
import sys
import os

def migrate_database():
    # Get the database path
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'nasiya_bro.db')
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(products)")
        columns = [column[1] for column in cursor.fetchall()]
        
        print(f"Current columns in products table: {columns}")
        
        # Add purchase_price column if it doesn't exist
        if 'purchase_price' not in columns:
            print("Adding purchase_price column...")
            cursor.execute("ALTER TABLE products ADD COLUMN purchase_price FLOAT")
            
        # Add sale_price column if it doesn't exist
        if 'sale_price' not in columns:
            print("Adding sale_price column...")
            cursor.execute("ALTER TABLE products ADD COLUMN sale_price FLOAT")
        
        # Copy existing price to sale_price for existing products
        if 'price' in columns:
            print("Migrating existing price data...")
            cursor.execute("""
                UPDATE products 
                SET sale_price = price, purchase_price = price * 0.8 
                WHERE sale_price IS NULL
            """)
        
        conn.commit()
        print("Migration completed successfully!")
        
        # Verify the changes
        cursor.execute("PRAGMA table_info(products)")
        columns = [column[1] for column in cursor.fetchall()]
        print(f"Updated columns in products table: {columns}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Migration failed: {e}")
        if 'conn' in locals():
            conn.close()
        return False

if __name__ == "__main__":
    print("Starting product pricing fields migration...")
    success = migrate_database()
    sys.exit(0 if success else 1)