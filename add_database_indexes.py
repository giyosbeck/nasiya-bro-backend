#!/usr/bin/env python3
"""
Database performance optimization script
Adds critical indexes for better query performance
"""

import sqlite3
import os

def add_indexes():
    """Add performance indexes to the database"""
    db_path = "nasiya_bro.db"
    
    if not os.path.exists(db_path):
        print(f"Database {db_path} not found!")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    indexes = [
        # User table indexes
        "CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone)",
        "CREATE INDEX IF NOT EXISTS idx_users_magazine_status ON users(magazine_id, status)",
        "CREATE INDEX IF NOT EXISTS idx_users_role ON users(role)",
        "CREATE INDEX IF NOT EXISTS idx_users_manager_id ON users(manager_id)",
        
        # Product table indexes
        "CREATE INDEX IF NOT EXISTS idx_products_magazine ON products(magazine_id)",
        "CREATE INDEX IF NOT EXISTS idx_products_name ON products(name)",
        
        # Sales table indexes
        "CREATE INDEX IF NOT EXISTS idx_sales_seller_date ON sales(seller_id, created_at)",
        "CREATE INDEX IF NOT EXISTS idx_sales_product ON sales(product_id)",
        "CREATE INDEX IF NOT EXISTS idx_sales_date ON sales(created_at)",
        
        # Loans table indexes
        "CREATE INDEX IF NOT EXISTS idx_loans_seller_date ON loans(seller_id, created_at)",
        "CREATE INDEX IF NOT EXISTS idx_loans_client ON loans(client_id)",
        "CREATE INDEX IF NOT EXISTS idx_loans_product ON loans(product_id)",
        "CREATE INDEX IF NOT EXISTS idx_loans_status ON loans(status)",
        "CREATE INDEX IF NOT EXISTS idx_loans_date ON loans(created_at)",
        
        # Clients table indexes
        "CREATE INDEX IF NOT EXISTS idx_clients_passport ON clients(passport_series)",
        "CREATE INDEX IF NOT EXISTS idx_clients_manager ON clients(manager_id)",
        "CREATE INDEX IF NOT EXISTS idx_clients_phone ON clients(phone)",
        
        # Transactions table indexes
        "CREATE INDEX IF NOT EXISTS idx_transactions_seller_date ON transactions(seller_id, created_at)",
        "CREATE INDEX IF NOT EXISTS idx_transactions_type ON transactions(type)",
        "CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(created_at)",
        
        # Magazine table indexes
        "CREATE INDEX IF NOT EXISTS idx_magazines_status ON magazines(status)",
        "CREATE INDEX IF NOT EXISTS idx_magazines_name ON magazines(name)",
    ]
    
    print("Adding database indexes for performance optimization...")
    
    for index_sql in indexes:
        try:
            cursor.execute(index_sql)
            index_name = index_sql.split("idx_")[1].split(" ")[0]
            print(f"✓ Added index: idx_{index_name}")
        except Exception as e:
            print(f"✗ Failed to add index: {e}")
    
    conn.commit()
    conn.close()
    print("Database indexing completed!")

if __name__ == "__main__":
    add_indexes()