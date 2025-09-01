#!/usr/bin/env python3
"""
Add notification tables to the database
"""

import sqlite3
import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def create_notification_tables(db_path="nasiya_bro.db"):
    """Create notification tables in the database"""
    
    # SQL to create notification tables
    create_tables_sql = """
    -- Create push_tokens table
    CREATE TABLE IF NOT EXISTS push_tokens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        token TEXT NOT NULL UNIQUE,
        user_id INTEGER NOT NULL,
        device_type TEXT DEFAULT 'mobile' CHECK (device_type IN ('mobile', 'web')),
        is_active BOOLEAN DEFAULT 1,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME,
        FOREIGN KEY (user_id) REFERENCES users (id)
    );
    
    -- Create notifications table
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT NOT NULL CHECK (type IN (
            'new_user_registration',
            'payment_overdue', 
            'loan_approved',
            'loan_rejected',
            'payment_reminder'
        )),
        title TEXT NOT NULL,
        body TEXT NOT NULL,
        data TEXT, -- JSON data stored as TEXT
        recipient_user_id INTEGER,
        recipient_role TEXT,
        sender_user_id INTEGER,
        push_token_id INTEGER,
        status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'sent', 'failed', 'delivered')),
        sent_at DATETIME,
        delivered_at DATETIME,
        error_message TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME,
        FOREIGN KEY (recipient_user_id) REFERENCES users (id),
        FOREIGN KEY (sender_user_id) REFERENCES users (id),
        FOREIGN KEY (push_token_id) REFERENCES push_tokens (id)
    );
    
    -- Create notification_preferences table
    CREATE TABLE IF NOT EXISTS notification_preferences (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        notification_type TEXT NOT NULL CHECK (notification_type IN (
            'new_user_registration',
            'payment_overdue',
            'loan_approved', 
            'loan_rejected',
            'payment_reminder'
        )),
        is_enabled BOOLEAN DEFAULT 1,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME,
        FOREIGN KEY (user_id) REFERENCES users (id),
        UNIQUE (user_id, notification_type)
    );
    
    -- Create indexes for better performance
    CREATE INDEX IF NOT EXISTS idx_push_tokens_user_id ON push_tokens(user_id);
    CREATE INDEX IF NOT EXISTS idx_push_tokens_active ON push_tokens(is_active);
    CREATE INDEX IF NOT EXISTS idx_notifications_recipient ON notifications(recipient_user_id);
    CREATE INDEX IF NOT EXISTS idx_notifications_status ON notifications(status);
    CREATE INDEX IF NOT EXISTS idx_notifications_type ON notifications(type);
    CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications(created_at);
    CREATE INDEX IF NOT EXISTS idx_notification_preferences_user ON notification_preferences(user_id);
    """
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print(f"Creating notification tables in {db_path}...")
        
        # Execute all SQL statements
        cursor.executescript(create_tables_sql)
        
        # Commit changes
        conn.commit()
        
        print("✅ Notification tables created successfully!")
        
        # Verify tables were created
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%notification%' OR name='push_tokens'")
        tables = cursor.fetchall()
        print(f"📋 Created tables: {[table[0] for table in tables]}")
        
        # Close connection
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating notification tables: {str(e)}")
        return False

def main():
    """Main function"""
    print("🚀 Starting notification tables migration...")
    
    # Check if database exists
    db_path = "nasiya_bro.db"
    if not os.path.exists(db_path):
        print(f"❌ Database file {db_path} not found!")
        sys.exit(1)
    
    # Create backup
    import shutil
    from datetime import datetime
    
    backup_path = f"nasiya_bro_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    shutil.copy2(db_path, backup_path)
    print(f"💾 Created backup: {backup_path}")
    
    # Create notification tables
    success = create_notification_tables(db_path)
    
    if success:
        print("✅ Notification system migration completed successfully!")
        print("\n🎯 Next steps:")
        print("1. Install httpx: pip install httpx")
        print("2. Restart your backend server")
        print("3. Test notification endpoints")
    else:
        print("❌ Migration failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()