#!/usr/bin/env python3
"""
Add track_payments column to loans table.

Safe for both SQLite (legacy) and PostgreSQL (dev/prod).
Idempotent — skips if column already exists.
"""
import sys
from sqlalchemy import create_engine, inspect, text
from app.core.config import settings


def has_column(engine, table_name: str, column_name: str) -> bool:
    inspector = inspect(engine)
    columns = [c["name"] for c in inspector.get_columns(table_name)]
    return column_name in columns


def main() -> int:
    engine = create_engine(settings.DATABASE_URL)
    dialect = engine.dialect.name
    print(f"Connected to {dialect} database")

    if has_column(engine, "loans", "track_payments"):
        print("Column 'track_payments' already exists — skipping")
        return 0

    print("Adding 'track_payments' column to loans table...")
    with engine.begin() as conn:
        if dialect == "postgresql":
            conn.execute(text(
                "ALTER TABLE loans ADD COLUMN track_payments BOOLEAN "
                "NOT NULL DEFAULT FALSE"
            ))
        else:
            conn.execute(text(
                "ALTER TABLE loans ADD COLUMN track_payments BOOLEAN "
                "NOT NULL DEFAULT 0"
            ))

    if has_column(engine, "loans", "track_payments"):
        print("✅ Column added successfully")
        return 0
    print("❌ Column not found after migration")
    return 1


if __name__ == "__main__":
    sys.exit(main())
