#!/usr/bin/env python3
"""
Automated SQLite to PostgreSQL Migration Script for Nasiya Bro
This script handles everything:
1. PostgreSQL user/database creation
2. Data migration from SQLite to PostgreSQL  
3. Schema validation
4. Configuration updates
"""

import os
import sys
import json
import sqlite3
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, date

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PostgreSQLMigrator:
    def __init__(self):
        self.sqlite_db_path = "nasiya_bro.db"
        self.postgres_config = {
            'host': 'localhost',
            'port': '5432',
            'database': 'nasiya_bro',
            'username': 'nasiya_user',
            'password': 'NasiyaBro2025!',
            'admin_user': 'postgres',
            'admin_password': None  # Will be set by user
        }
        
        # Table mapping with data type conversions
        self.table_mappings = {
            'users': {
                'columns': [
                    'id', 'name', 'phone', 'password_hash', 'role', 
                    'status', 'magazine_name', 'subscription_end_date', 
                    'created_at', 'updated_at', 'magazine_id', 'manager_id'
                ],
                'primary_key': 'id'
            },
            'clients': {
                'columns': [
                    'id', 'name', 'phone', 'passport_series', 
                    'passport_image_url', 'passport_image_urls',
                    'created_at', 'updated_at', 'manager_id'
                ],
                'primary_key': 'id'
            },
            'products': {
                'columns': [
                    'id', 'name', 'model', 'price', 'purchase_price', 
                    'sale_price', 'count', 'created_at', 'updated_at', 'manager_id'
                ],
                'primary_key': 'id'
            },
            'magazines': {
                'columns': [
                    'id', 'name', 'description', 'address', 'phone',
                    'status', 'subscription_end_date', 'approved_by',
                    'created_at', 'updated_at'
                ],
                'primary_key': 'id'
            },
            'sales': {
                'columns': [
                    'id', 'sale_price', 'sale_date', 'created_at',
                    'product_id', 'seller_id', 'magazine_id'
                ],
                'primary_key': 'id'
            },
            'loans': {
                'columns': [
                    'id', 'loan_price', 'initial_payment', 'remaining_amount',
                    'loan_months', 'interest_rate', 'monthly_payment',
                    'loan_start_date', 'video_url', 'agreement_images',
                    'is_completed', 'created_at', 'product_id', 'client_id',
                    'seller_id', 'magazine_id'
                ],
                'primary_key': 'id'
            },
            'loan_payments': {
                'columns': [
                    'id', 'amount', 'payment_date', 'due_date', 'status',
                    'is_late', 'is_full_payment', 'notes', 'created_at', 'loan_id'
                ],
                'primary_key': 'id'
            },
            'transactions': {
                'columns': [
                    'id', 'type', 'amount', 'description', 'created_at',
                    'sale_id', 'loan_id', 'loan_payment_id', 'product_id',
                    'client_id', 'seller_id', 'magazine_id'
                ],
                'primary_key': 'id'
            }
        }

    def check_prerequisites(self):
        """Check if PostgreSQL is installed and running"""
        logger.info("Checking prerequisites...")
        
        try:
            result = subprocess.run(['psql', '--version'], capture_output=True, text=True)
            if result.returncode != 0:
                logger.error("PostgreSQL is not installed or not in PATH")
                return False
            logger.info(f"PostgreSQL found: {result.stdout.strip()}")
        except FileNotFoundError:
            logger.error("PostgreSQL is not installed")
            return False
            
        # Check if SQLite database exists
        if not os.path.exists(self.sqlite_db_path):
            logger.error(f"SQLite database not found: {self.sqlite_db_path}")
            return False
            
        return True

    def install_requirements(self):
        """Install required Python packages"""
        logger.info("Installing required packages...")
        
        # Try multiple PostgreSQL adapters for compatibility
        adapters = ['psycopg2-binary', 'psycopg2', 'asyncpg']
        adapter_installed = False
        
        for adapter in adapters:
            try:
                subprocess.run([sys.executable, '-m', 'pip', 'install', adapter, '--no-cache-dir'], 
                             check=True, capture_output=True, text=True)
                logger.info(f"Installed {adapter}")
                adapter_installed = True
                break
            except subprocess.CalledProcessError:
                logger.warning(f"Failed to install {adapter}, trying next...")
                continue
        
        if not adapter_installed:
            logger.error("Failed to install any PostgreSQL adapter")
            return False
        
        # Install SQLAlchemy
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'sqlalchemy>=2.0.0'], 
                         check=True, capture_output=True)
            logger.info("Installed SQLAlchemy")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install SQLAlchemy: {e}")
            return False
            
        return True

    def setup_postgresql_user_and_database(self):
        """Create PostgreSQL user and database"""
        logger.info("Setting up PostgreSQL user and database...")
        
        # Get admin password
        admin_pass = input("Enter PostgreSQL admin (postgres) password (or press Enter if no password): ")
        self.postgres_config['admin_password'] = admin_pass if admin_pass else None
        
        # Connection parameters for admin user
        conn_params = {
            'host': self.postgres_config['host'],
            'port': self.postgres_config['port'],
            'user': self.postgres_config['admin_user'],
            'password': self.postgres_config['admin_password']
        }
        
        try:
            # Connect as admin user
            conn = psycopg2.connect(**conn_params)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()
            
            # Create user if not exists
            cursor.execute(f"""
                SELECT 1 FROM pg_roles WHERE rolname='{self.postgres_config['username']}';
            """)
            
            if not cursor.fetchone():
                cursor.execute(f"""
                    CREATE USER {self.postgres_config['username']} 
                    WITH PASSWORD '{self.postgres_config['password']}';
                """)
                logger.info(f"Created user: {self.postgres_config['username']}")
            else:
                logger.info(f"User {self.postgres_config['username']} already exists")
            
            # Create database if not exists
            cursor.execute(f"""
                SELECT 1 FROM pg_database WHERE datname='{self.postgres_config['database']}';
            """)
            
            if not cursor.fetchone():
                cursor.execute(f"""
                    CREATE DATABASE {self.postgres_config['database']} 
                    OWNER {self.postgres_config['username']};
                """)
                logger.info(f"Created database: {self.postgres_config['database']}")
            else:
                logger.info(f"Database {self.postgres_config['database']} already exists")
            
            # Grant privileges
            cursor.execute(f"""
                GRANT ALL PRIVILEGES ON DATABASE {self.postgres_config['database']} 
                TO {self.postgres_config['username']};
            """)
            
            cursor.close()
            conn.close()
            
            logger.info("PostgreSQL setup completed successfully")
            return True
            
        except psycopg2.Error as e:
            logger.error(f"PostgreSQL setup failed: {e}")
            return False

    def create_postgresql_schema(self):
        """Create tables in PostgreSQL using SQLAlchemy models"""
        logger.info("Creating PostgreSQL schema...")
        
        postgres_url = f"postgresql://{self.postgres_config['username']}:{self.postgres_config['password']}@{self.postgres_config['host']}:{self.postgres_config['port']}/{self.postgres_config['database']}"
        
        try:
            # Import models to create schema
            sys.path.append(os.path.dirname(os.path.abspath(__file__)))
            from app.models import user, product, transaction, magazine
            from app.db.database import Base
            
            engine = create_engine(postgres_url)
            Base.metadata.create_all(bind=engine)
            
            logger.info("PostgreSQL schema created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create PostgreSQL schema: {e}")
            return False

    def get_sqlite_data(self, table_name: str) -> List[Dict[str, Any]]:
        """Extract data from SQLite table"""
        conn = sqlite3.connect(self.sqlite_db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.OperationalError as e:
            logger.warning(f"Table {table_name} not found or error: {e}")
            return []
        finally:
            conn.close()

    def convert_data_types(self, data: Dict[str, Any], table_name: str) -> Dict[str, Any]:
        """Convert SQLite data types to PostgreSQL compatible types"""
        converted = {}
        
        for key, value in data.items():
            if value is None:
                converted[key] = None
            elif isinstance(value, str) and key.endswith('_date'):
                # Convert date strings to proper format
                try:
                    if 'T' in value:  # datetime format
                        dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                        converted[key] = dt
                    else:  # date format
                        dt = datetime.strptime(value, '%Y-%m-%d').date()
                        converted[key] = dt
                except (ValueError, TypeError):
                    converted[key] = value
            else:
                converted[key] = value
        
        return converted

    def migrate_table_data(self, table_name: str):
        """Migrate data from SQLite to PostgreSQL for a specific table"""
        logger.info(f"Migrating table: {table_name}")
        
        # Get SQLite data
        sqlite_data = self.get_sqlite_data(table_name)
        if not sqlite_data:
            logger.warning(f"No data found in SQLite table: {table_name}")
            return True
        
        postgres_url = f"postgresql://{self.postgres_config['username']}:{self.postgres_config['password']}@{self.postgres_config['host']}:{self.postgres_config['port']}/{self.postgres_config['database']}"
        
        try:
            engine = create_engine(postgres_url)
            
            with engine.begin() as conn:
                # Clear existing data
                conn.execute(text(f"TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE"))
                
                # Insert data
                table_config = self.table_mappings[table_name]
                columns = table_config['columns']
                
                for row_data in sqlite_data:
                    # Convert data types
                    converted_data = self.convert_data_types(row_data, table_name)
                    
                    # Filter only existing columns
                    filtered_data = {k: v for k, v in converted_data.items() if k in columns}
                    
                    if filtered_data:
                        placeholders = ', '.join(f":{key}" for key in filtered_data.keys())
                        column_names = ', '.join(filtered_data.keys())
                        
                        query = f"INSERT INTO {table_name} ({column_names}) VALUES ({placeholders})"
                        conn.execute(text(query), filtered_data)
                
                logger.info(f"Migrated {len(sqlite_data)} rows to {table_name}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to migrate table {table_name}: {e}")
            return False

    def migrate_all_data(self):
        """Migrate all table data from SQLite to PostgreSQL"""
        logger.info("Starting data migration...")
        
        postgres_url = f"postgresql://{self.postgres_config['username']}:{self.postgres_config['password']}@{self.postgres_config['host']}:{self.postgres_config['port']}/{self.postgres_config['database']}"
        
        try:
            engine = create_engine(postgres_url)
            sqlite_conn = sqlite3.connect(self.sqlite_db_path)
            sqlite_conn.row_factory = sqlite3.Row
            
            with engine.begin() as conn:
                # Clear all tables first
                tables_to_clear = ['transactions', 'loan_payments', 'loans', 'sales', 'products', 'clients', 'magazines', 'users']
                for table in tables_to_clear:
                    try:
                        conn.execute(text(f"DELETE FROM {table}"))
                    except:
                        pass
                
                # Migrate users first (without magazine_id to avoid circular dependency)
                users_data = list(sqlite_conn.execute("SELECT * FROM users").fetchall())
                user_magazine_refs = {}
                
                if users_data:
                    for row in users_data:
                        row_data = dict(row)
                        user_magazine_refs[row_data['id']] = row_data.get('magazine_id')
                        row_data['magazine_id'] = None  # Temporarily remove
                        
                        cols = ', '.join(row_data.keys())
                        vals = ', '.join([f':{k}' for k in row_data.keys()])
                        conn.execute(text(f"INSERT INTO users ({cols}) VALUES ({vals})"), row_data)
                    
                    logger.info(f"Users: {len(users_data)} rows migrated")
                
                # Migrate magazines
                magazines_data = list(sqlite_conn.execute("SELECT * FROM magazines").fetchall())
                if magazines_data:
                    for row in magazines_data:
                        row_data = dict(row)
                        cols = ', '.join(row_data.keys())
                        vals = ', '.join([f':{k}' for k in row_data.keys()])
                        conn.execute(text(f"INSERT INTO magazines ({cols}) VALUES ({vals})"), row_data)
                    
                    logger.info(f"Magazines: {len(magazines_data)} rows migrated")
                
                # Update users with magazine_id
                for user_id, mag_id in user_magazine_refs.items():
                    if mag_id:
                        conn.execute(text("UPDATE users SET magazine_id = :mid WHERE id = :uid"), 
                                   {'mid': mag_id, 'uid': user_id})
                
                # Migrate remaining tables
                remaining_tables = ['clients', 'products', 'sales', 'loans', 'loan_payments', 'transactions']
                
                for table_name in remaining_tables:
                    try:
                        rows = list(sqlite_conn.execute(f"SELECT * FROM {table_name}").fetchall())
                        if not rows:
                            logger.info(f"Table {table_name}: 0 rows (empty)")
                            continue
                        
                        for row in rows:
                            row_data = dict(row)
                            
                            # Fix boolean fields for PostgreSQL
                            if table_name == 'loans' and 'is_completed' in row_data:
                                row_data['is_completed'] = bool(row_data['is_completed'])
                            elif table_name == 'loan_payments':
                                if 'is_late' in row_data:
                                    row_data['is_late'] = bool(row_data['is_late'])
                                if 'is_full_payment' in row_data:
                                    row_data['is_full_payment'] = bool(row_data['is_full_payment'])
                            
                            # Convert date strings
                            for key, value in row_data.items():
                                if isinstance(value, str) and ('_date' in key or '_at' in key):
                                    if 'T' in value or ' ' in value:
                                        try:
                                            from datetime import datetime
                                            row_data[key] = datetime.fromisoformat(value.replace('Z', '+00:00'))
                                        except:
                                            pass
                            
                            cols = ', '.join(row_data.keys())
                            vals = ', '.join([f':{k}' for k in row_data.keys()])
                            conn.execute(text(f"INSERT INTO {table_name} ({cols}) VALUES ({vals})"), row_data)
                        
                        logger.info(f"Table {table_name}: {len(rows)} rows migrated")
                        
                    except Exception as e:
                        logger.error(f"Failed to migrate table {table_name}: {e}")
                        continue
                
                sqlite_conn.close()
                
            logger.info("Data migration completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            return False

    def update_sequences(self):
        """Update PostgreSQL sequences after data migration"""
        logger.info("Updating PostgreSQL sequences...")
        
        postgres_url = f"postgresql://{self.postgres_config['username']}:{self.postgres_config['password']}@{self.postgres_config['host']}:{self.postgres_config['port']}/{self.postgres_config['database']}"
        
        try:
            engine = create_engine(postgres_url)
            
            with engine.begin() as conn:
                for table_name in self.table_mappings.keys():
                    # Update sequence for each table
                    conn.execute(text(f"""
                        SELECT setval(pg_get_serial_sequence('{table_name}', 'id'), 
                                      COALESCE(MAX(id), 1)) 
                        FROM {table_name};
                    """))
                    
            logger.info("Sequences updated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update sequences: {e}")
            return False

    def update_backend_config(self):
        """Update backend configuration files for PostgreSQL"""
        logger.info("Updating backend configuration...")
        
        postgres_url = f"postgresql://{self.postgres_config['username']}:{self.postgres_config['password']}@{self.postgres_config['host']}:{self.postgres_config['port']}/{self.postgres_config['database']}"
        
        # Update config.py
        config_path = "app/core/config.py"
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                content = f.read()
            
            # Replace DATABASE_URL
            updated_content = content.replace(
                'DATABASE_URL: str = "sqlite:///./nasiya_bro.db"',
                f'DATABASE_URL: str = "{postgres_url}"'
            )
            
            with open(config_path, 'w') as f:
                f.write(updated_content)
            
            logger.info("Updated config.py")
        
        # Create .env file with PostgreSQL settings
        env_content = f"""
# Database Configuration
DATABASE_URL={postgres_url}
POSTGRES_HOST={self.postgres_config['host']}
POSTGRES_PORT={self.postgres_config['port']}
POSTGRES_DB={self.postgres_config['database']}
POSTGRES_USER={self.postgres_config['username']}
POSTGRES_PASSWORD={self.postgres_config['password']}

# Migration completed on {datetime.now().isoformat()}
"""
        
        with open(".env", "w") as f:
            f.write(env_content)
        
        logger.info("Created .env file with PostgreSQL configuration")
        return True

    def verify_migration(self):
        """Verify the migration was successful"""
        logger.info("Verifying migration...")
        
        postgres_url = f"postgresql://{self.postgres_config['username']}:{self.postgres_config['password']}@{self.postgres_config['host']}:{self.postgres_config['port']}/{self.postgres_config['database']}"
        
        try:
            engine = create_engine(postgres_url)
            
            # Check each table
            with engine.begin() as conn:
                for table_name in self.table_mappings.keys():
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                    count = result.scalar()
                    logger.info(f"Table {table_name}: {count} rows")
            
            logger.info("Migration verification completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Migration verification failed: {e}")
            return False

    def create_backup(self):
        """Create backup of SQLite database"""
        backup_name = f"nasiya_bro_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        try:
            subprocess.run(['cp', self.sqlite_db_path, backup_name], check=True)
            logger.info(f"Created backup: {backup_name}")
            return True
        except subprocess.CalledProcessError:
            logger.error("Failed to create backup")
            return False

    def run_migration(self):
        """Run the complete migration process"""
        logger.info("Starting PostgreSQL migration process...")
        
        print("\n" + "="*60)
        print("NASIYA BRO - SQLite to PostgreSQL Migration")
        print("="*60)
        
        steps = [
            ("Checking prerequisites", self.check_prerequisites),
            ("Installing requirements", self.install_requirements),
            ("Creating backup", self.create_backup),
            ("Setting up PostgreSQL", self.setup_postgresql_user_and_database),
            ("Creating schema", self.create_postgresql_schema),
            ("Migrating data", self.migrate_all_data),
            ("Updating sequences", self.update_sequences),
            ("Updating configuration", self.update_backend_config),
            ("Verifying migration", self.verify_migration)
        ]
        
        for step_name, step_function in steps:
            print(f"\n[STEP] {step_name}...")
            if not step_function():
                print(f"[FAILED] {step_name}")
                return False
            print(f"[SUCCESS] {step_name}")
        
        print("\n" + "="*60)
        print("MIGRATION COMPLETED SUCCESSFULLY!")
        print("="*60)
        print(f"Database: postgresql://{self.postgres_config['username']}:***@{self.postgres_config['host']}:{self.postgres_config['port']}/{self.postgres_config['database']}")
        print("Configuration updated in app/core/config.py and .env")
        print("\nNext steps:")
        print("1. Test your application: python run.py")
        print("2. Verify all features work correctly")
        print("3. Update any remaining hardcoded SQLite references")
        print("="*60)
        
        return True

def main():
    """Main entry point"""
    migrator = PostgreSQLMigrator()
    
    try:
        success = migrator.run_migration()
        if success:
            sys.exit(0)
        else:
            sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Migration cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()