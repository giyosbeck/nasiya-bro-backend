#!/usr/bin/env python3
"""
Database migration script to create the transactions table.
Run this script to add the transactions table to your existing database.
"""

import sqlite3
from pathlib import Path

def create_transactions_table():
    """Create the transactions table in the database."""
    db_path = Path(__file__).parent / "nasiya_bro.db"
    
    if not db_path.exists():
        print(f"Database file not found at {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create transactions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL CHECK (type IN ('sale', 'loan', 'loan_payment', 'product_restock', 'refund')),
                amount REAL NOT NULL,
                description TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                sale_id INTEGER,
                loan_id INTEGER,
                loan_payment_id INTEGER,
                product_id INTEGER,
                client_id INTEGER,
                seller_id INTEGER NOT NULL,
                magazine_id INTEGER NOT NULL,
                FOREIGN KEY (sale_id) REFERENCES sales (id),
                FOREIGN KEY (loan_id) REFERENCES loans (id),
                FOREIGN KEY (loan_payment_id) REFERENCES loan_payments (id),
                FOREIGN KEY (product_id) REFERENCES products (id),
                FOREIGN KEY (client_id) REFERENCES clients (id),
                FOREIGN KEY (seller_id) REFERENCES users (id),
                FOREIGN KEY (magazine_id) REFERENCES magazines (id)
            )
        ''')
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_type ON transactions (type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_created_at ON transactions (created_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_magazine_id ON transactions (magazine_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_seller_id ON transactions (seller_id)')
        
        conn.commit()
        print("✅ Transactions table created successfully!")
        
        # Check if table was created
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='transactions'")
        if cursor.fetchone():
            print("✅ Table 'transactions' confirmed in database")
        else:
            print("❌ Table 'transactions' not found after creation")
            
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("Creating transactions table...")
    success = create_transactions_table()
    if success:
        print("\n🎉 Migration completed successfully!")
        print("You can now restart your FastAPI server to use the new transactions functionality.")
    else:
        print("\n❌ Migration failed!")