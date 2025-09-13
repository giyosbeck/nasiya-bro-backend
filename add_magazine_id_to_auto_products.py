#!/usr/bin/env python3

import sys
import os
from sqlalchemy import create_engine, text

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.core.config import settings

def add_magazine_id_to_auto_products():
    """Add magazine_id column to auto_products table"""
    
    engine = create_engine(settings.DATABASE_URL)
    
    try:
        with engine.connect() as connection:
            # Add the magazine_id column
            print("Adding magazine_id column to auto_products table...")
            connection.execute(text("""
                ALTER TABLE auto_products 
                ADD COLUMN IF NOT EXISTS magazine_id INTEGER REFERENCES magazines(id);
            """))
            
            # Update existing auto_products to have magazine_id from their manager
            print("Updating existing auto_products with magazine_id from their manager...")
            connection.execute(text("""
                UPDATE auto_products 
                SET magazine_id = users.magazine_id 
                FROM users 
                WHERE auto_products.manager_id = users.id 
                AND auto_products.magazine_id IS NULL;
            """))
            
            # Make magazine_id NOT NULL after setting values
            connection.execute(text("""
                ALTER TABLE auto_products 
                ALTER COLUMN magazine_id SET NOT NULL;
            """))
            
            connection.commit()
            print("✅ Successfully added magazine_id column to auto_products table")
            
    except Exception as e:
        print(f"❌ Error updating auto_products table: {e}")
        sys.exit(1)

if __name__ == "__main__":
    add_magazine_id_to_auto_products()