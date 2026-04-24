"""Idempotent migration: add users.language column."""
from sqlalchemy import create_engine, text
from app.core.config import settings


def main() -> None:
    engine = create_engine(settings.DATABASE_URL)
    print("Connected to", engine.url.drivername)
    with engine.begin() as conn:
        exists = conn.execute(text(
            "SELECT 1 FROM information_schema.columns "
            "WHERE table_name='users' AND column_name='language'"
        )).first()
        if exists:
            print("users.language already exists — skip")
            return
        conn.execute(text("ALTER TABLE users ADD COLUMN language VARCHAR(2) NULL"))
        print("✅ users.language added (VARCHAR(2), NULL)")


if __name__ == "__main__":
    main()
