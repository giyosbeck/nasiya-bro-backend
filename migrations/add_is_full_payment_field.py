#!/usr/bin/env python3

import sqlite3
import sys
import os

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def add_is_full_payment_field():
    """Add is_full_payment field to loan_payments table"""
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'nasiya_bro.db')
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if column already exists
        cursor.execute("PRAGMA table_info(loan_payments)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'is_full_payment' not in columns:
            print("Adding is_full_payment column to loan_payments table...")
            
            # Add the column with default value False
            cursor.execute("""
                ALTER TABLE loan_payments 
                ADD COLUMN is_full_payment BOOLEAN DEFAULT 0
            """)
            
            print("✓ Successfully added is_full_payment column")
        else:
            print("✓ is_full_payment column already exists")
        
        # Commit changes
        conn.commit()
        print("✓ Migration completed successfully")
        
    except sqlite3.Error as e:
        print(f"✗ Database error: {e}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    finally:
        if conn:
            conn.close()
    
    return True

if __name__ == "__main__":
    add_is_full_payment_field()