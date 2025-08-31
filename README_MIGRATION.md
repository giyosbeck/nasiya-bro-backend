# PostgreSQL Migration Guide

## Overview
Complete automated migration from SQLite to PostgreSQL for the Nasiya Bro backend.

## What the Migration Does
✅ **Automatic PostgreSQL Setup**: Creates user `nasiya_user` and database `nasiya_bro`  
✅ **Complete Data Migration**: Transfers all tables and data from SQLite  
✅ **Schema Recreation**: Uses SQLAlchemy models to create PostgreSQL schema  
✅ **Configuration Updates**: Updates `config.py` and creates `.env` file  
✅ **Data Integrity**: Verifies all data transferred correctly  
✅ **Backup Creation**: Creates SQLite backup before migration  

## Quick Start
```bash
cd backend
./run_migration.sh
```

## Manual Migration
```bash
cd backend
pip install -r requirements_postgresql.txt
python3 migrate_to_postgresql.py
```

## Migration Details

### Database Credentials
- **Database**: `nasiya_bro`
- **User**: `nasiya_user` 
- **Password**: `NasiyaBro2025!`
- **Host**: `localhost`
- **Port**: `5432`

### Tables Migrated
1. `magazines` - Magazine/store information
2. `users` - Admin, managers, sellers
3. `clients` - Customer information  
4. `products` - Product catalog
5. `sales` - Sales transactions
6. `loans` - Installment loans
7. `loan_payments` - Payment tracking
8. `transactions` - All transaction records

### What Gets Updated
- `app/core/config.py` - Database URL changed to PostgreSQL
- `.env` file created with PostgreSQL settings
- `app/db/database.py` - Enhanced with PostgreSQL optimizations

## Prerequisites
- PostgreSQL installed and running
- Python 3.x
- Admin access to PostgreSQL (postgres user)

## Installation Commands

### macOS
```bash
brew install postgresql
brew services start postgresql
```

### Ubuntu/Debian  
```bash
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql
```

### CentOS/RHEL
```bash
sudo yum install postgresql postgresql-server
sudo systemctl start postgresql
```

## Verification
After migration, verify with:
```bash
python3 run.py
```

The backend should start normally and all API endpoints should work.

## Rollback
If needed, restore from backup:
```bash
# SQLite backup created as: nasiya_bro_backup_YYYYMMDD_HHMMSS.db
cp nasiya_bro_backup_*.db nasiya_bro.db
# Revert config.py to use SQLite URL
```

## Production Notes
- Change default passwords before production
- Configure PostgreSQL for performance
- Set up proper backup schedule
- Update connection pooling settings

## Support
All migration steps are logged. Check console output for detailed progress.