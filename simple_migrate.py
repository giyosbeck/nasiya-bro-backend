#!/usr/bin/env python3
"""
Simple PostgreSQL Migration Script for Nasiya Bro
Assumes PostgreSQL is already running and accessible
"""

import os
import sys
import sqlite3
import logging
from datetime import datetime

# Add current directory to path to import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class SimpleMigrator:
    def __init__(self):
        self.sqlite_path = "nasiya_bro.db"
        
        # PostgreSQL connection (update these as needed)
        self.pg_host = "localhost"
        self.pg_port = "5432"
        self.pg_database = "nasiya_bro"
        self.pg_user = "nasiya_user" 
        self.pg_password = "NasiyaBro2025!"
        
        self.pg_url = f"postgresql://{self.pg_user}:{self.pg_password}@{self.pg_host}:{self.pg_port}/{self.pg_database}"

    def setup_postgresql(self):
        """Setup PostgreSQL database and user using command line"""
        logger.info("Setting up PostgreSQL database...")
        
        # Commands to run as postgres user
        commands = [
            f"CREATE USER {self.pg_user} WITH PASSWORD '{self.pg_password}';",
            f"CREATE DATABASE {self.pg_database} OWNER {self.pg_user};",
            f"GRANT ALL PRIVILEGES ON DATABASE {self.pg_database} TO {self.pg_user};"
        ]
        
        print("\nRun these PostgreSQL commands as admin:")
        print("sudo -u postgres psql")
        print("Then execute:")
        for cmd in commands:
            print(f"  {cmd}")
        print("  \\q")
        
        input("\nPress Enter after running the above commands...")
        return True

    def migrate_data(self):
        """Migrate data from SQLite to PostgreSQL"""
        logger.info("Starting data migration...")
        
        # Connect to SQLite
        sqlite_conn = sqlite3.connect(self.sqlite_path)
        sqlite_conn.row_factory = sqlite3.Row
        
        # Connect to PostgreSQL
        pg_engine = create_engine(self.pg_url)
        
        # Get table list from SQLite
        tables_query = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        tables = [row[0] for row in sqlite_conn.execute(tables_query).fetchall()]
        
        logger.info(f"Found tables: {', '.join(tables)}")
        
        # Import models to create schema
        try:
            from app.models import user, product, transaction, magazine
            from app.db.database import Base
            
            # Create all tables
            Base.metadata.create_all(bind=pg_engine)
            logger.info("Created PostgreSQL schema")
        except Exception as e:
            logger.error(f"Failed to create schema: {e}")
            return False
        
        # Migrate each table
        with pg_engine.begin() as pg_conn:
            for table in tables:
                try:
                    # Get SQLite data
                    rows = list(sqlite_conn.execute(f"SELECT * FROM {table}").fetchall())
                    if not rows:
                        logger.info(f"Table {table}: 0 rows (empty)")
                        continue
                    
                    # Clear PostgreSQL table
                    pg_conn.execute(text(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE"))
                    
                    # Get column names
                    columns = [description[0] for description in rows[0].keys()]
                    
                    # Insert data
                    placeholders = ', '.join([f":{col}" for col in columns])
                    column_names = ', '.join(columns)
                    
                    insert_query = f"INSERT INTO {table} ({column_names}) VALUES ({placeholders})"
                    
                    for row in rows:
                        row_dict = dict(row)
                        # Convert date strings for PostgreSQL
                        for key, value in row_dict.items():
                            if isinstance(value, str) and ('_date' in key or '_at' in key):
                                if 'T' in value or ' ' in value:
                                    try:
                                        row_dict[key] = datetime.fromisoformat(value.replace('Z', '+00:00'))
                                    except:
                                        pass
                        
                        pg_conn.execute(text(insert_query), row_dict)
                    
                    logger.info(f"Table {table}: {len(rows)} rows migrated")
                    
                except Exception as e:
                    logger.error(f"Failed to migrate table {table}: {e}")
                    continue
        
        sqlite_conn.close()
        
        # Update sequences
        with pg_engine.begin() as pg_conn:
            for table in tables:
                try:
                    pg_conn.execute(text(f"""
                        SELECT setval(pg_get_serial_sequence('{table}', 'id'), 
                                      COALESCE(MAX(id), 1)) 
                        FROM {table};
                    """))
                except:
                    pass  # Skip tables without id column
        
        logger.info("Migration completed successfully!")
        return True

    def update_config(self):
        """Update configuration files"""
        logger.info("Updating configuration...")
        
        # Update config.py
        config_path = "app/core/config.py"
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                content = f.read()
            
            content = content.replace(
                'DATABASE_URL: str = "sqlite:///./nasiya_bro.db"',
                f'DATABASE_URL: str = "{self.pg_url}"'
            )
            
            with open(config_path, 'w') as f:
                f.write(content)
            
            logger.info("Updated config.py")
        
        # Create .env
        with open(".env", "w") as f:
            f.write(f"DATABASE_URL={self.pg_url}\n")
        
        logger.info("Created .env file")
        return True

def main():
    migrator = SimpleMigrator()
    
    print("=" * 50)
    print("NASIYA BRO - Simple PostgreSQL Migration")
    print("=" * 50)
    
    try:
        migrator.setup_postgresql()
        migrator.migrate_data()
        migrator.update_config()
        
        print("\n" + "=" * 50)
        print("MIGRATION COMPLETED!")
        print("=" * 50)
        print(f"Database: {migrator.pg_database}")
        print(f"User: {migrator.pg_user}")
        print("Test with: python run.py")
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()