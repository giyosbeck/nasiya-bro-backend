#!/usr/bin/env python3
"""
One-shot demo seed for testing the new mobile app end-to-end.

Creates:
- 1 admin user            (phone: +998900000001, password: admin1234)
- 1 GADGETS manager       (phone: +998900000002, password: manager1234)
  owns magazine "Demo Store" with:
    - 5 products in stock
    - 3 clients with passport series
- 1 AUTO manager          (phone: +998900000003, password: auto1234)
  with one car product

Run from the backend folder:

    source venv/bin/activate
    python -m scripts.seed_demo

Idempotent: re-running updates existing records rather than duplicating.
"""

from datetime import date, timedelta
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.db.database import SessionLocal
from app.db.init_db import init_db  # loads all models so SA mapper resolves
from app.models.user import User, UserRole, UserStatus, UserType, Client
from app.models.magazine import Magazine, MagazineStatus
from app.models.product import Product
from app.models.auto_product import AutoProduct

# Force-load models referenced by relationships so SQLAlchemy can resolve them
import app.models.auto_transaction  # noqa: F401
import app.models.transaction  # noqa: F401


pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")


def upsert_user(
    db: Session,
    *,
    phone: str,
    password: str,
    name: str,
    role: UserRole,
    user_type: UserType | None = None,
    magazine_id: int | None = None,
    subscription_months: int = 12,
) -> User:
    user = db.query(User).filter(User.phone == phone).first()
    end = date.today() + timedelta(days=subscription_months * 30)
    if user:
        user.name = name
        user.password_hash = pwd.hash(password)
        user.role = role
        user.status = UserStatus.ACTIVE
        user.user_type = user_type
        user.magazine_id = magazine_id
        user.subscription_end_date = end
    else:
        user = User(
            phone=phone,
            password_hash=pwd.hash(password),
            name=name,
            role=role,
            status=UserStatus.ACTIVE,
            user_type=user_type,
            magazine_id=magazine_id,
            subscription_end_date=end,
        )
        db.add(user)
    db.flush()
    return user


def upsert_magazine(db: Session, *, name: str) -> Magazine:
    mag = db.query(Magazine).filter(Magazine.name == name).first()
    end = date.today() + timedelta(days=365)
    if mag:
        mag.status = MagazineStatus.ACTIVE
        mag.subscription_end_date = end
    else:
        mag = Magazine(name=name, status=MagazineStatus.ACTIVE, subscription_end_date=end)
        db.add(mag)
    db.flush()
    return mag


def seed_products(db: Session, manager_id: int) -> None:
    specs = [
        ("iPhone 15 Pro", "A3102", 12_000_000, 14_500_000, 5),
        ("iPhone 14", "A2882", 9_500_000, 11_200_000, 3),
        ("Samsung Galaxy S24", "SM-S921", 9_000_000, 10_800_000, 4),
        ("Xiaomi Redmi Note 13", "23124RA7EO", 2_800_000, 3_400_000, 12),
        ("AirPods Pro 2", "MTJV3", 2_200_000, 2_800_000, 8),
    ]
    for name, model, buy, sale, count in specs:
        existing = (
            db.query(Product)
            .filter(Product.manager_id == manager_id, Product.name == name)
            .first()
        )
        if existing:
            existing.model = model
            existing.price = sale
            existing.purchase_price = buy
            existing.sale_price = sale
            existing.count = count
        else:
            db.add(
                Product(
                    name=name,
                    model=model,
                    price=sale,
                    purchase_price=buy,
                    sale_price=sale,
                    count=count,
                    manager_id=manager_id,
                )
            )


def seed_clients(db: Session, manager_id: int) -> None:
    records = [
        ("Demo Client 1", "+998900111001", "AA1234567"),
        ("Demo Client 2", "+998900111002", "AB2345678"),
        ("Demo Client 3", "+998900111003", "AC3456789"),
    ]
    for name, phone, series in records:
        existing = db.query(Client).filter(Client.passport_series == series).first()
        if existing:
            existing.name = name
            existing.phone = phone
            existing.manager_id = manager_id
        else:
            db.add(
                Client(
                    name=name,
                    phone=phone,
                    passport_series=series,
                    manager_id=manager_id,
                )
            )


def seed_auto_product(db: Session, manager_id: int) -> None:
    existing = (
        db.query(AutoProduct)
        .filter(AutoProduct.manager_id == manager_id, AutoProduct.car_name == "Chevrolet Cobalt")
        .first()
    )
    if existing:
        return
    db.add(
        AutoProduct(
            car_name="Chevrolet Cobalt",
            model="LTZ",
            color="White",
            year=2024,
            purchase_price=140_000_000,
            sale_price=155_000_000,
            count=1,
            manager_id=manager_id,
        )
    )


def main() -> None:
    db = SessionLocal()
    try:
        print("Seeding demo data...")

        admin = upsert_user(
            db,
            phone="+998900000001",
            password="admin1234",
            name="Demo Admin",
            role=UserRole.ADMIN,
        )
        print(f"  admin user ready (id={admin.id}) phone=+998900000001 pwd=admin1234")

        magazine = upsert_magazine(db, name="Demo Store")
        print(f"  magazine ready (id={magazine.id}) name='Demo Store'")

        manager = upsert_user(
            db,
            phone="+998900000002",
            password="manager1234",
            name="Demo Manager",
            role=UserRole.MANAGER,
            user_type=UserType.GADGETS,
            magazine_id=magazine.id,
        )
        print(f"  GADGETS manager ready (id={manager.id}) phone=+998900000002 pwd=manager1234")

        seed_products(db, manager.id)
        print("  5 products seeded in Demo Store")

        seed_clients(db, manager.id)
        print("  3 clients seeded")

        auto_manager = upsert_user(
            db,
            phone="+998900000003",
            password="auto1234",
            name="Demo Auto Manager",
            role=UserRole.MANAGER,
            user_type=UserType.AUTO,
        )
        print(
            f"  AUTO manager ready (id={auto_manager.id}) phone=+998900000003 pwd=auto1234 "
            "(car seeding skipped — auto_products table needs magazine_id migration)"
        )

        db.commit()
        print("\n✓ Done. Login from the mobile app with any of the phones above.")
    except Exception as exc:
        db.rollback()
        print(f"✗ Seed failed: {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
