#!/usr/bin/env python3
"""
Database migration script to add passport_image_urls column to clients table
"""
import sqlite3
import os
import sys

def add_passport_image_urls_column():
    """Add passport_image_urls column to clients table"""
    
    # Database path
    db_path = "nasiya_bro.db"
    
    if not os.path.exists(db_path):
        print(f"Error: Database file {db_path} not found!")
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if column already exists
        cursor.execute("PRAGMA table_info(clients)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'passport_image_urls' in columns:
            print("Column 'passport_image_urls' already exists in clients table.")
            conn.close()
            return True
        
        # Add the new column
        print("Adding 'passport_image_urls' column to clients table...")
        cursor.execute("""
            ALTER TABLE clients 
            ADD COLUMN passport_image_urls TEXT
        """)
        
        # Commit changes
        conn.commit()
        
        # Verify the column was added
        cursor.execute("PRAGMA table_info(clients)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'passport_image_urls' in columns:
            print("✅ Successfully added 'passport_image_urls' column to clients table.")
            
            # Show table structure
            print("\nUpdated clients table structure:")
            cursor.execute("PRAGMA table_info(clients)")
            for row in cursor.fetchall():
                print(f"  {row[1]} ({row[2]})")
                
            conn.close()
            return True
        else:
            print("❌ Failed to add column.")
            conn.close()
            return False
            
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        if 'conn' in locals():
            conn.close()
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        if 'conn' in locals():
            conn.close()
        return False

if __name__ == "__main__":
    print("🔄 Starting database migration...")
    success = add_passport_image_urls_column()
    
    if success:
        print("✅ Migration completed successfully!")
        sys.exit(0)
    else:
        print("❌ Migration failed!")
        sys.exit(1)