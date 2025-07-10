#!/usr/bin/env python3
"""
Migration script to add magazine_id to Sales and Loans tables
"""
import sqlite3
from pathlib import Path

def migrate_database():
    db_path = Path("nasiya_bro.db")
    if not db_path.exists():
        print("Database file not found!")
        return
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        # Check if magazine_id columns already exist
        cursor.execute("PRAGMA table_info(sales)")
        sales_columns = [row[1] for row in cursor.fetchall()]
        
        cursor.execute("PRAGMA table_info(loans)")
        loans_columns = [row[1] for row in cursor.fetchall()]
        
        # Add magazine_id to sales table if it doesn't exist
        if 'magazine_id' not in sales_columns:
            print("Adding magazine_id column to sales table...")
            cursor.execute("ALTER TABLE sales ADD COLUMN magazine_id INTEGER")
            
            # Update existing sales with magazine_id based on seller's manager
            cursor.execute("""
                UPDATE sales 
                SET magazine_id = (
                    SELECT CASE 
                        WHEN u.role = 'manager' THEN u.id
                        WHEN u.role = 'seller' THEN u.manager_id
                        ELSE u.id
                    END
                    FROM users u 
                    WHERE u.id = sales.seller_id
                )
            """)
            print(f"Updated {cursor.rowcount} sales records with magazine_id")
        
        # Add magazine_id to loans table if it doesn't exist
        if 'magazine_id' not in loans_columns:
            print("Adding magazine_id column to loans table...")
            cursor.execute("ALTER TABLE loans ADD COLUMN magazine_id INTEGER")
            
            # Update existing loans with magazine_id based on seller's manager
            cursor.execute("""
                UPDATE loans 
                SET magazine_id = (
                    SELECT CASE 
                        WHEN u.role = 'manager' THEN u.id
                        WHEN u.role = 'seller' THEN u.manager_id
                        ELSE u.id
                    END
                    FROM users u 
                    WHERE u.id = loans.seller_id
                )
            """)
            print(f"Updated {cursor.rowcount} loan records with magazine_id")
        
        # Commit the changes
        conn.commit()
        print("Migration completed successfully!")
        
    except Exception as e:
        print(f"Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()