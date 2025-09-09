#!/usr/bin/env python3

import sys
import os
from sqlalchemy import text

# Add the parent directory to sys.path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import engine
from app.core.config import settings

def add_auto_system():
    """
    Add auto system support to the database:
    1. Add user_type column to users table
    2. Create auto_products table
    3. Create auto_sales table
    4. Create auto_loans table
    5. Create auto_loan_payments table
    """
    with engine.connect() as conn:
        try:
            print("🚀 Starting auto system migration...")
            
            # 1. Add user_type enum and column to users table
            print("📝 Adding user_type to users table...")
            
            # Create the enum type first
            conn.execute(text("""
                DO $$ BEGIN
                    CREATE TYPE usertype AS ENUM ('gadgets', 'auto');
                EXCEPTION
                    WHEN duplicate_object THEN null;
                END $$;
            """))
            
            # Add the column with default value
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS user_type usertype DEFAULT 'gadgets'::usertype;
            """))
            
            # 2. Create auto_products table
            print("🚗 Creating auto_products table...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS auto_products (
                    id SERIAL PRIMARY KEY,
                    car_name VARCHAR NOT NULL,
                    model VARCHAR NOT NULL,
                    color VARCHAR NOT NULL,
                    year INTEGER NOT NULL,
                    purchase_price FLOAT NOT NULL,
                    sale_price FLOAT NOT NULL,
                    count INTEGER DEFAULT 0,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE,
                    manager_id INTEGER NOT NULL REFERENCES users(id)
                );
            """))
            
            # Add indexes for auto_products
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_auto_products_car_name ON auto_products(car_name);
                CREATE INDEX IF NOT EXISTS idx_auto_products_manager_id ON auto_products(manager_id);
            """))
            
            # 3. Create auto_sales table
            print("💰 Creating auto_sales table...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS auto_sales (
                    id SERIAL PRIMARY KEY,
                    sale_price FLOAT NOT NULL,
                    sale_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    auto_product_id INTEGER NOT NULL REFERENCES auto_products(id),
                    seller_id INTEGER NOT NULL REFERENCES users(id),
                    magazine_id INTEGER NOT NULL REFERENCES magazines(id)
                );
            """))
            
            # 4. Create auto_loans table
            print("📄 Creating auto_loans table...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS auto_loans (
                    id SERIAL PRIMARY KEY,
                    loan_price FLOAT NOT NULL,
                    initial_payment FLOAT NOT NULL,
                    remaining_amount FLOAT NOT NULL,
                    loan_months INTEGER NOT NULL,
                    yearly_interest_rate FLOAT NOT NULL,
                    monthly_payment FLOAT NOT NULL,
                    loan_start_date TIMESTAMP WITH TIME ZONE NOT NULL,
                    video_url VARCHAR,
                    agreement_images TEXT,
                    is_completed BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    auto_product_id INTEGER NOT NULL REFERENCES auto_products(id),
                    client_id INTEGER NOT NULL REFERENCES clients(id),
                    seller_id INTEGER NOT NULL REFERENCES users(id),
                    magazine_id INTEGER NOT NULL REFERENCES magazines(id)
                );
            """))
            
            # 5. Create auto_loan_payments table
            print("💳 Creating auto_loan_payments table...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS auto_loan_payments (
                    id SERIAL PRIMARY KEY,
                    amount FLOAT NOT NULL,
                    payment_date TIMESTAMP WITH TIME ZONE,
                    due_date TIMESTAMP WITH TIME ZONE NOT NULL,
                    status paymentstatus DEFAULT 'pending',
                    is_late BOOLEAN DEFAULT FALSE,
                    is_full_payment BOOLEAN DEFAULT FALSE,
                    notes TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    auto_loan_id INTEGER NOT NULL REFERENCES auto_loans(id)
                );
            """))
            
            # Add indexes for performance
            print("🔍 Creating indexes...")
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_auto_sales_auto_product_id ON auto_sales(auto_product_id);
                CREATE INDEX IF NOT EXISTS idx_auto_sales_seller_id ON auto_sales(seller_id);
                CREATE INDEX IF NOT EXISTS idx_auto_sales_sale_date ON auto_sales(sale_date);
                
                CREATE INDEX IF NOT EXISTS idx_auto_loans_auto_product_id ON auto_loans(auto_product_id);
                CREATE INDEX IF NOT EXISTS idx_auto_loans_client_id ON auto_loans(client_id);
                CREATE INDEX IF NOT EXISTS idx_auto_loans_seller_id ON auto_loans(seller_id);
                CREATE INDEX IF NOT EXISTS idx_auto_loans_loan_start_date ON auto_loans(loan_start_date);
                
                CREATE INDEX IF NOT EXISTS idx_auto_loan_payments_auto_loan_id ON auto_loan_payments(auto_loan_id);
                CREATE INDEX IF NOT EXISTS idx_auto_loan_payments_due_date ON auto_loan_payments(due_date);
                CREATE INDEX IF NOT EXISTS idx_auto_loan_payments_status ON auto_loan_payments(status);
            """))
            
            # Update existing users to have gadgets type by default
            print("👥 Updating existing users to gadgets type...")
            conn.execute(text("""
                UPDATE users 
                SET user_type = 'gadgets'::usertype 
                WHERE user_type IS NULL;
            """))
            
            # Commit all changes
            conn.commit()
            
            print("✅ Auto system migration completed successfully!")
            print("\nNew tables created:")
            print("  - auto_products (car inventory)")
            print("  - auto_sales (car sales)")  
            print("  - auto_loans (car financing)")
            print("  - auto_loan_payments (payment tracking)")
            print("\nUsers table updated:")
            print("  - Added user_type column (gadgets/auto)")
            print("  - All existing users set to 'gadgets' type")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            raise

if __name__ == "__main__":
    add_auto_system()