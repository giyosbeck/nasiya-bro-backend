from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.magazine import Magazine, MagazineStatus
from app.models.user import User, UserRole, UserStatus
from app.db.database import SessionLocal
import logging

logger = logging.getLogger(__name__)

def check_and_deactivate_expired_magazines() -> dict:
    """
    Background task to check for expired magazine subscriptions and deactivate them.
    Returns a dictionary with the results of the operation.
    """
    db = SessionLocal()
    try:
        today = date.today()
        
        # Find expired magazines
        expired_magazines = db.query(Magazine).filter(
            and_(
                Magazine.status == MagazineStatus.ACTIVE,
                Magazine.subscription_end_date < today
            )
        ).all()
        
        deactivated_count = 0
        deactivated_magazines = []
        
        for magazine in expired_magazines:
            magazine.status = MagazineStatus.INACTIVE
            
            # Also deactivate the manager
            manager = db.query(User).filter(
                User.magazine_id == magazine.id,
                User.role == UserRole.MANAGER
            ).first()
            
            if manager:
                manager.status = UserStatus.INACTIVE
            
            deactivated_magazines.append({
                "id": magazine.id,
                "name": magazine.name,
                "subscription_end_date": magazine.subscription_end_date.isoformat(),
                "manager_name": manager.name if manager else None
            })
            deactivated_count += 1
            
            logger.info(f"Deactivated expired magazine: {magazine.name} (ID: {magazine.id})")
        
        db.commit()
        
        result = {
            "success": True,
            "message": f"Deactivated {deactivated_count} expired magazines",
            "deactivated_magazines": deactivated_magazines,
            "total_deactivated": deactivated_count,
            "check_date": today.isoformat()
        }
        
        logger.info(f"Magazine expiration check completed: {result['message']}")
        return result
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error during magazine expiration check: {str(e)}")
        return {
            "success": False,
            "message": f"Error during magazine expiration check: {str(e)}",
            "total_deactivated": 0,
            "check_date": date.today().isoformat()
        }
    finally:
        db.close()

def get_magazines_expiring_soon(days: int = 7) -> dict:
    """
    Get magazines whose subscriptions are expiring within the specified number of days.
    """
    db = SessionLocal()
    try:
        today = date.today()
        cutoff_date = today + timedelta(days=days)
        
        expiring_magazines = db.query(Magazine).filter(
            and_(
                Magazine.status == MagazineStatus.ACTIVE,
                Magazine.subscription_end_date <= cutoff_date,
                Magazine.subscription_end_date >= today
            )
        ).all()
        
        result = {
            "success": True,
            "message": f"Found {len(expiring_magazines)} magazines expiring within {days} days",
            "expiring_magazines": [
                {
                    "id": magazine.id,
                    "name": magazine.name,
                    "subscription_end_date": magazine.subscription_end_date.isoformat(),
                    "days_remaining": (magazine.subscription_end_date - today).days
                }
                for magazine in expiring_magazines
            ],
            "total_expiring": len(expiring_magazines),
            "check_date": today.isoformat()
        }
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting expiring magazines: {str(e)}")
        return {
            "success": False,
            "message": f"Error getting expiring magazines: {str(e)}",
            "total_expiring": 0,
            "check_date": date.today().isoformat()
        }
    finally:
        db.close()