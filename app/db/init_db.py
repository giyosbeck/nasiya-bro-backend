from sqlalchemy.orm import Session
from app.db.database import engine, SessionLocal, Base
from app.models.user import User, UserRole, UserStatus
from app.models.product import Product
from app.models.transaction import Sale, Loan, LoanPayment
from app.models.user import Client
from app.core.config import settings
from app.core.security import get_password_hash

def init_db() -> None:
    """
    Initialize database with tables and default admin user
    """
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create default admin user if not exists
    db = SessionLocal()
    try:
        admin = db.query(User).filter(
            User.phone == "+998" + settings.DEFAULT_ADMIN_USERNAME
        ).first()
        
        if not admin:
            admin_user = User(
                name="Admin",
                phone="+998" + settings.DEFAULT_ADMIN_USERNAME,
                password_hash=get_password_hash(settings.DEFAULT_ADMIN_PASSWORD),
                role=UserRole.ADMIN,
                status=UserStatus.ACTIVE
            )
            db.add(admin_user)
            db.commit()
            print("Default admin user created")
        else:
            print("Admin user already exists")
    
    except Exception as e:
        print(f"Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close() 