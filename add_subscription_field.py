"""
Migration script to add subscription_end_date field to existing users table.
Run this script once to update the database schema.
"""
import sqlite3
from pathlib import Path

def add_subscription_field():
    """Add subscription_end_date column to users table if it doesn't exist."""
    
    # Path to the database file
    db_path = Path("nasiya_bro.db")
    
    if not db_path.exists():
        print(f"Database file not found at {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if the column already exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'subscription_end_date' in columns:
            print("Column 'subscription_end_date' already exists in users table")
            return
        
        # Add the new column
        cursor.execute("""
            ALTER TABLE users 
            ADD COLUMN subscription_end_date DATE
        """)
        
        conn.commit()
        print("Successfully added 'subscription_end_date' column to users table")
        
        # Verify the column was added
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        print(f"Current columns in users table: {columns}")
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    add_subscription_field()