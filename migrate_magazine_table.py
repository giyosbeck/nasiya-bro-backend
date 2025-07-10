#!/usr/bin/env python3
"""
Comprehensive migration script to create Magazine table and restructure database
"""
import sqlite3
from pathlib import Path

def migrate_to_magazine_table():
    db_path = Path("nasiya_bro.db")
    if not db_path.exists():
        print("Database file not found!")
        return
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        print("Starting magazine table migration...")
        
        # Step 1: Create magazines table
        print("1. Creating magazines table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS magazines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR NOT NULL UNIQUE,
                description TEXT,
                address VARCHAR,
                phone VARCHAR,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME
            )
        """)
        
        # Step 2: Insert unique magazine names from existing users
        print("2. Populating magazines from existing users...")
        cursor.execute("""
            INSERT OR IGNORE INTO magazines (name, created_at)
            SELECT DISTINCT magazine_name, datetime('now')
            FROM users 
            WHERE magazine_name IS NOT NULL AND magazine_name != ''
        """)
        print(f"   Created {cursor.rowcount} magazine records")
        
        # Step 3: Add magazine_id column to users table if it doesn't exist
        cursor.execute("PRAGMA table_info(users)")
        user_columns = [row[1] for row in cursor.fetchall()]
        
        if 'magazine_id' not in user_columns:
            print("3. Adding magazine_id column to users table...")
            cursor.execute("ALTER TABLE users ADD COLUMN magazine_id INTEGER")
        else:
            print("3. magazine_id column already exists in users table")
        
        # Step 4: Update users with magazine_id
        print("4. Updating users with magazine_id...")
        cursor.execute("""
            UPDATE users 
            SET magazine_id = (
                SELECT m.id 
                FROM magazines m 
                WHERE m.name = users.magazine_name
            )
            WHERE magazine_name IS NOT NULL AND magazine_name != ''
        """)
        print(f"   Updated {cursor.rowcount} user records with magazine_id")
        
        # Step 5: Update sales table magazine_id column to reference magazines table
        print("5. Updating sales table magazine_id to reference magazines...")
        cursor.execute("""
            UPDATE sales 
            SET magazine_id = (
                SELECT u.magazine_id
                FROM users u 
                WHERE u.id = sales.seller_id
            )
            WHERE magazine_id IS NOT NULL
        """)
        print(f"   Updated {cursor.rowcount} sales records")
        
        # Step 6: Update loans table magazine_id column to reference magazines table
        print("6. Updating loans table magazine_id to reference magazines...")
        cursor.execute("""
            UPDATE loans 
            SET magazine_id = (
                SELECT u.magazine_id
                FROM users u 
                WHERE u.id = loans.seller_id
            )
            WHERE magazine_id IS NOT NULL
        """)
        print(f"   Updated {cursor.rowcount} loan records")
        
        # Step 7: Verify the migration
        print("7. Verifying migration results...")
        
        # Check magazines
        cursor.execute("SELECT COUNT(*) FROM magazines")
        magazine_count = cursor.fetchone()[0]
        print(f"   Total magazines: {magazine_count}")
        
        # Check users with magazine_id
        cursor.execute("SELECT COUNT(*) FROM users WHERE magazine_id IS NOT NULL")
        users_with_magazine = cursor.fetchone()[0]
        print(f"   Users with magazine_id: {users_with_magazine}")
        
        # Check sales with magazine_id
        cursor.execute("SELECT COUNT(*) FROM sales WHERE magazine_id IS NOT NULL")
        sales_with_magazine = cursor.fetchone()[0]
        print(f"   Sales with magazine_id: {sales_with_magazine}")
        
        # Check loans with magazine_id
        cursor.execute("SELECT COUNT(*) FROM loans WHERE magazine_id IS NOT NULL")
        loans_with_magazine = cursor.fetchone()[0]
        print(f"   Loans with magazine_id: {loans_with_magazine}")
        
        # Step 8: Display magazine summary
        print("8. Magazine summary:")
        cursor.execute("""
            SELECT m.id, m.name, COUNT(u.id) as user_count
            FROM magazines m
            LEFT JOIN users u ON m.id = u.magazine_id
            GROUP BY m.id, m.name
            ORDER BY m.name
        """)
        
        for row in cursor.fetchall():
            print(f"   Magazine ID {row[0]}: '{row[1]}' ({row[2]} users)")
        
        # Commit all changes
        conn.commit()
        print("\n✅ Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_to_magazine_table()