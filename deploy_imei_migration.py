#!/usr/bin/env python3
"""
Production deployment script for IMEI migration.
Run this on your deployed server to add IMEI functionality.
"""

import sys
import os

# Add the app directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from sqlalchemy import text, inspect, create_engine
    from app.core.config import settings
    print("✅ SQLAlchemy modules loaded successfully")
except ImportError as e:
    print(f"❌ Missing required modules: {e}")
    print("📦 Installing required dependencies...")
    import subprocess
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'sqlalchemy', 'psycopg2-binary'])
    print("✅ Dependencies installed, restarting script...")
    from sqlalchemy import text, inspect, create_engine
    from app.core.config import settings

def check_database_connection():
    """Test database connection"""
    try:
        # Use settings from your app
        if hasattr(settings, 'DATABASE_URL'):
            db_url = settings.DATABASE_URL
        else:
            # Fallback to environment variable
            db_url = os.getenv('DATABASE_URL', 'sqlite:///./nasiya_bro.db')
        
        print(f"🔗 Testing connection to: {db_url.split('@')[0] if '@' in db_url else db_url}")
        
        engine = create_engine(db_url)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            print("✅ Database connection successful")
            return engine, db_url
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return None, None

def add_imei_fields(engine, db_url):
    """Add IMEI fields to database"""
    db_type = 'postgresql' if 'postgres' in db_url.lower() else 'sqlite'
    print(f"🔍 Database type: {db_type.upper()}")
    
    try:
        with engine.connect() as conn:
            # Check if fields already exist
            inspector = inspect(engine)
            
            sales_columns = [col['name'] for col in inspector.get_columns('sales')]
            loans_columns = [col['name'] for col in inspector.get_columns('loans')]
            
            sales_has_imei = 'imei' in sales_columns
            loans_has_imei = 'imei' in loans_columns
            
            if sales_has_imei and loans_has_imei:
                print("✅ IMEI fields already exist in both tables")
                return True
            
            print("📝 Adding IMEI fields...")
            
            # Add IMEI columns based on database type
            if db_type == 'postgresql':
                if not sales_has_imei:
                    conn.execute(text("ALTER TABLE sales ADD COLUMN IF NOT EXISTS imei VARCHAR(20);"))
                    print("   ✅ Added IMEI to sales table")
                
                if not loans_has_imei:
                    conn.execute(text("ALTER TABLE loans ADD COLUMN IF NOT EXISTS imei VARCHAR(20);"))
                    print("   ✅ Added IMEI to loans table")
                
                # Create indexes
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_sales_imei ON sales(imei);"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_loans_imei ON loans(imei);"))
                print("   ✅ Created indexes")
                
            else:  # SQLite
                if not sales_has_imei:
                    conn.execute(text("ALTER TABLE sales ADD COLUMN imei VARCHAR(20);"))
                    print("   ✅ Added IMEI to sales table")
                
                if not loans_has_imei:
                    conn.execute(text("ALTER TABLE loans ADD COLUMN imei VARCHAR(20);"))
                    print("   ✅ Added IMEI to loans table")
                
                # Create indexes (SQLite syntax)
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_sales_imei ON sales(imei);"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_loans_imei ON loans(imei);"))
                print("   ✅ Created indexes")
            
            conn.commit()
            print("🎉 Migration completed successfully!")
            return True
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

def main():
    """Main execution function"""
    print("🚀 Nasiya Bro - IMEI Migration Tool")
    print("=" * 50)
    
    # Test database connection
    engine, db_url = check_database_connection()
    if not engine:
        print("\n💡 Solutions:")
        print("1. Make sure your database server is running")
        print("2. Check DATABASE_URL in your .env file")
        print("3. Verify database credentials")
        return False
    
    # Run migration
    success = add_imei_fields(engine, db_url)
    
    if success:
        print("\n🎉 IMEI functionality is now available!")
        print("📱 Features enabled:")
        print("   • IMEI tracking in loan creation")
        print("   • IMEI tracking in sales") 
        print("   • Device history tracking")
    else:
        print("\n❌ Migration failed. Please check the errors above.")
    
    return success

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️  Migration cancelled")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)