#!/usr/bin/env python3
"""
Create audit_logs table. Idempotent, supports SQLite + PostgreSQL.
"""
import sys
from sqlalchemy import create_engine, inspect, text
from app.core.config import settings


def has_table(engine, name: str) -> bool:
    inspector = inspect(engine)
    return name in inspector.get_table_names()


def main() -> int:
    engine = create_engine(settings.DATABASE_URL)
    dialect = engine.dialect.name
    print(f"Connected to {dialect}")

    if has_table(engine, "audit_logs"):
        print("audit_logs already exists — skipping")
        return 0

    print("Creating audit_logs table...")
    with engine.begin() as conn:
        if dialect == "postgresql":
            conn.execute(text(
                """
                CREATE TABLE audit_logs (
                    id SERIAL PRIMARY KEY,
                    actor_user_id INTEGER NOT NULL REFERENCES users(id),
                    action VARCHAR(64) NOT NULL,
                    target_user_id INTEGER REFERENCES users(id),
                    metadata_json TEXT,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                )
                """
            ))
            conn.execute(text("CREATE INDEX ix_audit_logs_actor_user_id ON audit_logs (actor_user_id)"))
            conn.execute(text("CREATE INDEX ix_audit_logs_action ON audit_logs (action)"))
            conn.execute(text("CREATE INDEX ix_audit_logs_target_user_id ON audit_logs (target_user_id)"))
            conn.execute(text("CREATE INDEX ix_audit_logs_created_at ON audit_logs (created_at)"))
        else:
            conn.execute(text(
                """
                CREATE TABLE audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    actor_user_id INTEGER NOT NULL,
                    action TEXT NOT NULL,
                    target_user_id INTEGER,
                    metadata_json TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (actor_user_id) REFERENCES users (id),
                    FOREIGN KEY (target_user_id) REFERENCES users (id)
                )
                """
            ))

    print("✅ audit_logs created")
    return 0


if __name__ == "__main__":
    sys.exit(main())
