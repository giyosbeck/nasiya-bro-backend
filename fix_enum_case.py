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
            
            # First check what enum values actually exist
            result = conn.execute(text("""
                SELECT e.enumlabel 
                FROM pg_enum e 
                JOIN pg_type t ON e.enumtypid = t.oid 
                WHERE t.typname = 'usertype'
                ORDER BY e.enumsortorder;
            """))
            
            enum_values = [row[0] for row in result.fetchall()]
            print(f"Actual usertype enum values: {enum_values}")
            
            # Check current user_type values
            result = conn.execute(text("""
                SELECT user_type, COUNT(*) as count
                FROM users 
                WHERE user_type IS NOT NULL
                GROUP BY user_type
                ORDER BY user_type;
            """))
            
            current_values = result.fetchall()
            print(f"\nCurrent user_type values in database:")
            for value, count in current_values:
                print(f"  - '{value}': {count} users")
            
            # Determine correct enum values to use
            if not enum_values:
                print("❌ No usertype enum found!")
                return
            
            # Find the correct mappings
            gadgets_enum = None
            auto_enum = None
            
            for value in enum_values:
                if value.lower() == 'gadgets':
                    gadgets_enum = value
                elif value.lower() == 'auto':
                    auto_enum = value
            
            print(f"Mapping: 'gadgets' → '{gadgets_enum}', 'auto' → '{auto_enum}'")
            
            if not gadgets_enum:
                print("❌ No gadgets enum value found!")
                return
                
            print("\n📝 Updating user_type values to match enum...")
            
            # Update 'gadgets' to correct enum value
            result = conn.execute(text(f"""
                UPDATE users 
                SET user_type = '{gadgets_enum}'::usertype 
                WHERE user_type::text = 'gadgets';
            """))
            gadgets_updated = result.rowcount
            
            auto_updated = 0
            # Update 'auto' if it exists and we have a mapping
            if auto_enum:
                result = conn.execute(text(f"""
                    UPDATE users 
                    SET user_type = '{auto_enum}'::usertype 
                    WHERE user_type::text = 'auto';
                """))
                auto_updated = result.rowcount
            
            # Commit changes
            conn.commit()
            
            print(f"✅ Fixed enum case successfully!")
            print(f"  - Updated {gadgets_updated} users from 'gadgets' to '{gadgets_enum}'")
            if auto_enum:
                print(f"  - Updated {auto_updated} users from 'auto' to '{auto_enum}'")
            
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