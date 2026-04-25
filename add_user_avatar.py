"""Idempotent migration: add users.avatar_url column."""
from sqlalchemy import create_engine, text
from app.core.config import settings


def main() -> None:
    engine = create_engine(settings.DATABASE_URL)
    print("Connected to", engine.url.drivername)
    with engine.begin() as conn:
        exists = conn.execute(text(
            "SELECT 1 FROM information_schema.columns "
            "WHERE table_name='users' AND column_name='avatar_url'"
        )).first()
        if exists:
            print("users.avatar_url already exists — skip")
            return
        conn.execute(text("ALTER TABLE users ADD COLUMN avatar_url VARCHAR NULL"))
        print("✅ users.avatar_url added (VARCHAR, NULL)")


if __name__ == "__main__":
    main()
