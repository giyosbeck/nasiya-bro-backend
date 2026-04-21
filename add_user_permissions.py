#!/usr/bin/env python3
"""
Add can_see_purchase_price column to users table.

Idempotent, supports SQLite and PostgreSQL.
Defaults to TRUE for admin+manager (backwards compat), FALSE for seller.
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
    print(f"Connected to {dialect}")

    if has_column(engine, "users", "can_see_purchase_price"):
        print("Column already exists — skipping")
        return 0

    print("Adding can_see_purchase_price column...")
    with engine.begin() as conn:
        if dialect == "postgresql":
            conn.execute(text(
                "ALTER TABLE users ADD COLUMN can_see_purchase_price BOOLEAN "
                "NOT NULL DEFAULT FALSE"
            ))
            conn.execute(text(
                "UPDATE users SET can_see_purchase_price = TRUE "
                "WHERE role IN ('admin', 'manager')"
            ))
        else:
            conn.execute(text(
                "ALTER TABLE users ADD COLUMN can_see_purchase_price BOOLEAN "
                "NOT NULL DEFAULT 0"
            ))
            conn.execute(text(
                "UPDATE users SET can_see_purchase_price = 1 "
                "WHERE role IN ('admin', 'manager')"
            ))

    print("✅ Column added and admin/manager backfilled")
    return 0


if __name__ == "__main__":
    sys.exit(main())
