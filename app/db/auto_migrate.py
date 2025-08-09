"""
Auto-migration functionality to ensure database schema is up to date
This runs automatically when the app starts
"""
import sqlite3
import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def get_database_path():
    """Get the database file path"""
    # Try common locations for the database
    possible_paths = [
        "nasiya_bro.db",
        "../nasiya_bro.db", 
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "nasiya_bro.db")
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    # Default to the first option if none found
    return possible_paths[0]

def auto_migrate_database():
    """
    Automatically add missing columns and perform necessary migrations
    This ensures the app works even if database schema is outdated
    """
    db_path = get_database_path()
    
    try:
        # Check if database exists
        if not os.path.exists(db_path):
            logger.info(f"Database not found at {db_path}, will be created by SQLAlchemy")
            return True
        
        logger.info(f"Running auto-migration on database: {db_path}")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check and update products table
        cursor.execute("PRAGMA table_info(products)")
        columns = [column[1] for column in cursor.fetchall()]
        
        migrations_applied = []
        
        # Add purchase_price column if missing
        if 'purchase_price' not in columns:
            logger.info("Adding missing purchase_price column to products table")
            cursor.execute("ALTER TABLE products ADD COLUMN purchase_price FLOAT")
            migrations_applied.append("purchase_price column added")
            
        # Add sale_price column if missing  
        if 'sale_price' not in columns:
            logger.info("Adding missing sale_price column to products table")
            cursor.execute("ALTER TABLE products ADD COLUMN sale_price FLOAT")
            migrations_applied.append("sale_price column added")
        
        # Migrate existing data if new columns were added
        if migrations_applied:
            logger.info("Migrating existing product data...")
            cursor.execute("""
                UPDATE products 
                SET sale_price = COALESCE(sale_price, price),
                    purchase_price = COALESCE(purchase_price, price * 0.8)
                WHERE sale_price IS NULL OR purchase_price IS NULL
            """)
            migrations_applied.append("existing data migrated")
        
        # Add more migrations here as needed in the future
        # Example:
        # if 'new_column' not in columns:
        #     cursor.execute("ALTER TABLE products ADD COLUMN new_column TEXT")
        #     migrations_applied.append("new_column added")
        
        conn.commit()
        conn.close()
        
        if migrations_applied:
            logger.info(f"✅ Auto-migration completed: {', '.join(migrations_applied)}")
        else:
            logger.info("✅ Database schema is up to date, no migrations needed")
            
        return True
        
    except Exception as e:
        logger.error(f"❌ Auto-migration failed: {e}")
        # Don't fail the app startup, just log the error
        return False

def ensure_database_compatibility():
    """
    Ensure database is compatible with current code
    This is the main function called during app startup
    """
    try:
        return auto_migrate_database()
    except Exception as e:
        logger.error(f"Database compatibility check failed: {e}")
        # Return True so app doesn't fail to start
        return True