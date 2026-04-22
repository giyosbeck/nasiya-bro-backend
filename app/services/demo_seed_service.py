import random
import string
from sqlalchemy.orm import Session
from app.models.user import User, UserType, Client
from app.models.product import Product


GADGETS_PRODUCTS = [
    ("iPhone 15", "128GB Blue", 12_500_000, 14_500_000, 3),
    ("Samsung Galaxy S24", "256GB Black", 9_800_000, 11_500_000, 2),
]

AUTO_PRODUCTS = [
    ("Chevrolet Cobalt", "LT 2024", 135_000_000, 148_000_000, 2),
    ("Chevrolet Nexia 3", "LTZ 2024", 95_000_000, 105_000_000, 1),
]

DEMO_CLIENT_NAME = "Demo Mijoz"
DEMO_CLIENT_PHONE = "+998900000000"


def _rand_passport() -> str:
    letters = "".join(random.choices(string.ascii_uppercase, k=2))
    digits = "".join(random.choices(string.digits, k=7))
    return f"{letters}{digits}"


def seed_for_user(db: Session, user: User) -> None:
    """Create a small demo dataset for a newly registered user.

    Gives users something to look at on first open so the app does not feel
    empty. Items are tagged via their name prefix so users can identify and
    delete them. Failures are swallowed to keep registration robust.
    """
    try:
        products_spec = (
            GADGETS_PRODUCTS if user.user_type == UserType.GADGETS else AUTO_PRODUCTS
        )
        for name, model, purchase, sale, count in products_spec:
            db.add(
                Product(
                    name=name,
                    model=model,
                    price=sale,
                    purchase_price=purchase,
                    sale_price=sale,
                    count=count,
                    manager_id=user.id,
                )
            )

        db.add(
            Client(
                name=DEMO_CLIENT_NAME,
                phone=DEMO_CLIENT_PHONE + str(user.id),
                passport_series=_rand_passport(),
                manager_id=user.id,
            )
        )

        db.commit()
    except Exception:
        db.rollback()
