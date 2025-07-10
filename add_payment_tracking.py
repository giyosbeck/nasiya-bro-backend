#!/usr/bin/env python3
"""
Database migration to add payment tracking enhancements
- Add PaymentStatus enum and status column to loan_payments
- Make payment_date nullable for pending payments
- Update existing payments to have proper status
"""

import sqlite3
from pathlib import Path

def migrate_payment_tracking():
    db_path = Path(__file__).parent / "nasiya_bro.db"
    
    if not db_path.exists():
        print(f"Database not found at {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("Starting payment tracking migration...")
        
        # Step 1: Check current loan_payments table structure
        cursor.execute("PRAGMA table_info(loan_payments)")
        columns = [column[1] for column in cursor.fetchall()]
        print(f"Current columns: {columns}")
        
        # Step 2: Add status column if it doesn't exist
        if 'status' not in columns:
            print("Adding status column...")
            cursor.execute("""
                ALTER TABLE loan_payments 
                ADD COLUMN status TEXT DEFAULT 'pending'
            """)
        
        # Step 3: Create new table with updated structure
        print("Creating new loan_payments table...")
        cursor.execute("""
            CREATE TABLE loan_payments_new (
                id INTEGER PRIMARY KEY,
                amount REAL NOT NULL,
                payment_date TIMESTAMP NULL,  -- Now nullable
                due_date TIMESTAMP NOT NULL,
                status TEXT DEFAULT 'pending',
                is_late BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                loan_id INTEGER NOT NULL,
                FOREIGN KEY (loan_id) REFERENCES loans (id)
            )
        """)
        
        # Step 4: Copy existing data
        print("Copying existing payment data...")
        cursor.execute("""
            INSERT INTO loan_payments_new 
            (id, amount, payment_date, due_date, status, is_late, created_at, loan_id)
            SELECT 
                id, 
                amount, 
                CASE 
                    WHEN payment_date IS NOT NULL THEN payment_date
                    ELSE NULL 
                END as payment_date,
                due_date,
                CASE 
                    WHEN payment_date IS NOT NULL THEN 'paid'
                    WHEN due_date < datetime('now') THEN 'overdue'
                    ELSE 'pending'
                END as status,
                is_late,
                created_at,
                loan_id
            FROM loan_payments
        """)
        
        # Step 5: Drop old table and rename new one
        print("Replacing old table...")
        cursor.execute("DROP TABLE loan_payments")
        cursor.execute("ALTER TABLE loan_payments_new RENAME TO loan_payments")
        
        # Step 6: Get some statistics
        cursor.execute("SELECT COUNT(*) FROM loan_payments")
        total_payments = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM loan_payments WHERE status = 'pending'")
        pending_payments = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM loan_payments WHERE status = 'paid'")
        paid_payments = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM loan_payments WHERE status = 'overdue'")
        overdue_payments = cursor.fetchone()[0]
        
        print(f"\nMigration completed successfully!")
        print(f"Total payments: {total_payments}")
        print(f"Pending: {pending_payments}")
        print(f"Paid: {paid_payments}")
        print(f"Overdue: {overdue_payments}")
        
        conn.commit()
        
    except Exception as e:
        print(f"Migration failed: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_payment_tracking()