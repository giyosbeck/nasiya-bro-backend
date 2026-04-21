import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import bcrypt
from app.db.database import SessionLocal
from app.models.user import User

def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

TEST_PASSWORD = "test123456"

TARGET_PHONES = [
    "+998admin",
    "+998901234567",
    "+998910188181",
    "+998944221266",
]

def main():
    db = SessionLocal()
    try:
        new_hash = get_password_hash(TEST_PASSWORD)
        users = db.query(User).filter(User.phone.in_(TARGET_PHONES)).all()
        for u in users:
            u.password_hash = new_hash
            print(f"{u.role.value:8s} {u.status.value:8s} {u.phone:20s} {u.name}")
        db.commit()
        print(f"\nPassword for all above: {TEST_PASSWORD}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
