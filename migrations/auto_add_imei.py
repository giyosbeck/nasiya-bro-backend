#!/usr/bin/env python3
"""
Automatic IMEI fields migration script.
Detects database type and runs appropriate migration.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text, inspect
from app.db.database import engine
from app.core.config import settings

def detect_database_type():
    """Detect if using PostgreSQL or SQLite"""
    db_url = settings.DATABASE_URL.lower()
    if 'postgresql' in db_url or 'postgres' in db_url:
        return 'postgresql'
    elif 'sqlite' in db_url:
        return 'sqlite'
    else:
        return 'unknown'

def check_imei_fields_exist():
    """Check if IMEI fields already exist"""
    try:
        with engine.connect() as conn:
            inspector = inspect(engine)
            
            # Check sales table
            sales_columns = [col['name'] for col in inspector.get_columns('sales')]
            sales_has_imei = 'imei' in sales_columns
            
            # Check loans table
            loans_columns = [col['name'] for col in inspector.get_columns('loans')]
            loans_has_imei = 'imei' in loans_columns
            
            return sales_has_imei, loans_has_imei
    except Exception as e:
        print(f"❌ Error checking existing fields: {e}")
        return False, False

def add_imei_postgresql():
    """Add IMEI fields for PostgreSQL"""
    try:
        with engine.connect() as conn:
            print("📝 Adding IMEI field to sales table...")
            conn.execute(text("ALTER TABLE sales ADD COLUMN IF NOT EXISTS imei VARCHAR(20);"))
            
            print("📝 Adding IMEI field to loans table...")
            conn.execute(text("ALTER TABLE loans ADD COLUMN IF NOT EXISTS imei VARCHAR(20);"))
            
            print("📝 Creating indexes for IMEI fields...")
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_sales_imei ON sales(imei);"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_loans_imei ON loans(imei);"))
            
            conn.commit()
            return True
    except Exception as e:
        print(f"❌ PostgreSQL migration failed: {e}")
        return False

def add_imei_sqlite():
    """Add IMEI fields for SQLite"""
    try:
        with engine.connect() as conn:
            # SQLite doesn't support IF NOT EXISTS for ADD COLUMN, so check first
            sales_has_imei, loans_has_imei = check_imei_fields_exist()
            
            if not sales_has_imei:
                print("📝 Adding IMEI field to sales table...")
                conn.execute(text("ALTER TABLE sales ADD COLUMN imei VARCHAR(20);"))
            
            if not loans_has_imei:
                print("📝 Adding IMEI field to loans table...")
                conn.execute(text("ALTER TABLE loans ADD COLUMN imei VARCHAR(20);"))
            
            print("📝 Creating indexes for IMEI fields...")
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_sales_imei ON sales(imei);"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_loans_imei ON loans(imei);"))
            
            conn.commit()
            return True
    except Exception as e:
        print(f"❌ SQLite migration failed: {e}")
        return False

def main():
    """Main migration function"""
    print("🚀 Starting IMEI fields migration...")
    print(f"📊 Database URL: {settings.DATABASE_URL}")
    
    # Detect database type
    db_type = detect_database_type()
    print(f"🔍 Detected database type: {db_type.upper()}")
    
    # Check if fields already exist
    sales_has_imei, loans_has_imei = check_imei_fields_exist()
    
    if sales_has_imei and loans_has_imei:
        print("✅ IMEI fields already exist in both tables")
        print("🎉 No migration needed!")
        return True
    
    # Run appropriate migration
    success = False
    if db_type == 'postgresql':
        success = add_imei_postgresql()
    elif db_type == 'sqlite':
        success = add_imei_sqlite()
    else:
        print(f"❌ Unsupported database type: {db_type}")
        return False
    
    if success:
        print("\n🎉 Migration completed successfully!")
        print("✅ IMEI fields added to sales and loans tables")
        print("✅ Indexes created for performance")
        print("\n📱 You can now:")
        print("   • Create loans with IMEI codes")
        print("   • Record sales with IMEI codes") 
        print("   • Track devices through IMEI")
    else:
        print("\n❌ Migration failed!")
    
    return success

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️  Migration cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)