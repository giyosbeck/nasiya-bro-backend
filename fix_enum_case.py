#!/usr/bin/env python3

import sys
import os
from sqlalchemy import text

# Add the parent directory to sys.path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import engine

def fix_enum_case():
    """
    Fix the case mismatch between database enum values and user data:
    - Database enum: GADGETS, AUTO (uppercase)
    - User data: gadgets, auto (lowercase) 
    
    Update all user_type values to use uppercase to match the enum.
    """
    with engine.connect() as conn:
        try:
            print("🚀 Fixing enum case mismatch...")
            
            # Check current user_type values
            result = conn.execute(text("""
                SELECT user_type, COUNT(*) as count
                FROM users 
                WHERE user_type IS NOT NULL
                GROUP BY user_type
                ORDER BY user_type;
            """))
            
            current_values = result.fetchall()
            print(f"Current user_type values in database:")
            for value, count in current_values:
                print(f"  - '{value}': {count} users")
            
            # Update lowercase to uppercase to match enum
            print("\n📝 Updating user_type values to match enum...")
            
            # Update 'gadgets' to 'GADGETS'
            result = conn.execute(text("""
                UPDATE users 
                SET user_type = 'GADGETS'::usertype 
                WHERE user_type::text = 'gadgets';
            """))
            gadgets_updated = result.rowcount
            
            # Update 'auto' to 'AUTO' (in case any exist)
            result = conn.execute(text("""
                UPDATE users 
                SET user_type = 'AUTO'::usertype 
                WHERE user_type::text = 'auto';
            """))
            auto_updated = result.rowcount
            
            # Commit changes
            conn.commit()
            
            print(f"✅ Fixed enum case successfully!")
            print(f"  - Updated {gadgets_updated} users from 'gadgets' to 'GADGETS'")
            print(f"  - Updated {auto_updated} users from 'auto' to 'AUTO'")
            
            # Verify the fix
            result = conn.execute(text("""
                SELECT user_type, COUNT(*) as count
                FROM users 
                WHERE user_type IS NOT NULL
                GROUP BY user_type
                ORDER BY user_type;
            """))
            
            updated_values = result.fetchall()
            print(f"\nUpdated user_type values:")
            for value, count in updated_values:
                print(f"  - '{value}': {count} users")
                
        except Exception as e:
            print(f"❌ Fix failed: {e}")
            raise

if __name__ == "__main__":
    fix_enum_case()