"""
Quick fix script to run on your deployed server
This will add the missing database columns that are causing the Internal Server Error
"""

import sqlite3
import os

def fix_server_database():
    # Adjust this path to match your server's database location
    db_path = 'nasiya_bro.db'  # or wherever your database is on the server
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        print("Please adjust the db_path in this script to match your server setup")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check current columns
        cursor.execute("PRAGMA table_info(products)")
        columns = [column[1] for column in cursor.fetchall()]
        print(f"Current columns: {columns}")
        
        # Add missing columns if they don't exist
        if 'purchase_price' not in columns:
            print("Adding purchase_price column...")
            cursor.execute("ALTER TABLE products ADD COLUMN purchase_price FLOAT")
            
        if 'sale_price' not in columns:
            print("Adding sale_price column...")
            cursor.execute("ALTER TABLE products ADD COLUMN sale_price FLOAT")
        
        # Update existing products with the new fields
        print("Migrating existing data...")
        cursor.execute("""
            UPDATE products 
            SET sale_price = price, purchase_price = price * 0.8 
            WHERE sale_price IS NULL
        """)
        
        conn.commit()
        conn.close()
        
        print("✅ Database fixed successfully!")
        print("Now restart your server and the Internal Server Error should be gone.")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Fixing server database...")
    fix_server_database()