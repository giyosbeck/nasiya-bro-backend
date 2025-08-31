#!/usr/bin/env python3
"""
SQLAlchemy-based migration script to add IMEI fields to sales and loans tables.
Uses the same database connection as your FastAPI app.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.db.database import engine
from app.core.config import settings

def add_imei_fields():
    """Add IMEI fields to sales and loans tables using SQLAlchemy"""
    print(f"🔗 Using database: {settings.DATABASE_URL}")
    
    try:
        with engine.connect() as conn:
            print("✅ Database connection successful")
            
            # Add IMEI field to sales table
            print("📝 Adding IMEI field to sales table...")
            conn.execute(text("""
                ALTER TABLE sales 
                ADD COLUMN IF NOT EXISTS imei VARCHAR(20);
            """))
            
            # Add IMEI field to loans table  
            print("📝 Adding IMEI field to loans table...")
            conn.execute(text("""
                ALTER TABLE loans 
                ADD COLUMN IF NOT EXISTS imei VARCHAR(20);
            """))
            
            # Create indexes for IMEI searches
            print("📝 Creating indexes for IMEI fields...")
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_sales_imei ON sales(imei);
            """))
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_loans_imei ON loans(imei);
            """))
            
            # Commit changes
            conn.commit()
            print("✅ Successfully added IMEI fields to database")
            return True
            
    except Exception as e:
        print(f"❌ Error adding IMEI fields: {e}")
        return False

def rollback_imei_fields():
    """Rollback IMEI fields (for testing purposes)"""
    print(f"🔗 Using database: {settings.DATABASE_URL}")
    
    try:
        with engine.connect() as conn:
            print("✅ Database connection successful")
            
            print("🗑️  Removing IMEI fields...")
            conn.execute(text("ALTER TABLE sales DROP COLUMN IF EXISTS imei;"))
            conn.execute(text("ALTER TABLE loans DROP COLUMN IF EXISTS imei;"))
            conn.execute(text("DROP INDEX IF EXISTS idx_sales_imei;"))
            conn.execute(text("DROP INDEX IF EXISTS idx_loans_imei;"))
            
            conn.commit()
            print("✅ Successfully removed IMEI fields")
            return True
            
    except Exception as e:
        print(f"❌ Error removing IMEI fields: {e}")
        return False

def verify_imei_fields():
    """Verify IMEI fields exist in database"""
    try:
        with engine.connect() as conn:
            # Check sales table
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'sales' AND column_name = 'imei';
            """))
            sales_has_imei = len(result.fetchall()) > 0
            
            # Check loans table
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'loans' AND column_name = 'imei';
            """))
            loans_has_imei = len(result.fetchall()) > 0
            
            print("📊 IMEI Field Status:")
            print(f"   Sales table: {'✅ IMEI field exists' if sales_has_imei else '❌ IMEI field missing'}")
            print(f"   Loans table: {'✅ IMEI field exists' if loans_has_imei else '❌ IMEI field missing'}")
            
            return sales_has_imei and loans_has_imei
            
    except Exception as e:
        print(f"❌ Error verifying IMEI fields: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--rollback":
            rollback_imei_fields()
        elif sys.argv[1] == "--verify":
            verify_imei_fields()
        else:
            print("Usage:")
            print("  python migrations/add_imei_sqlalchemy.py          # Add IMEI fields")
            print("  python migrations/add_imei_sqlalchemy.py --verify # Check if fields exist")
            print("  python migrations/add_imei_sqlalchemy.py --rollback # Remove IMEI fields")
    else:
        success = add_imei_fields()
        if success:
            print("\n🎉 Migration completed! You can now:")
            print("   • Create loans with IMEI codes")
            print("   • Record sales with IMEI codes")
            print("   • Track devices through IMEI")