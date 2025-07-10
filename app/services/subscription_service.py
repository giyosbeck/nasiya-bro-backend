from datetime import date, timedelta
from sqlalchemy.orm import Session
from app.models.user import User, UserRole, UserStatus
from app.db.database import SessionLocal
import logging

logger = logging.getLogger(__name__)

def check_and_deactivate_expired_users() -> dict:
    """
    Background task to check for expired subscriptions and deactivate users.
    Returns a dictionary with the results of the operation.
    """
    db = SessionLocal()
    try:
        today = date.today()
        
        # Find all active users with expired subscriptions
        expired_users = db.query(User).filter(
            User.status == UserStatus.ACTIVE,
            User.subscription_end_date.isnot(None),
            User.subscription_end_date < today,
            User.role != UserRole.ADMIN  # Don't deactivate admin users
        ).all()
        
        deactivated_count = 0
        deactivated_users = []
        
        for user in expired_users:
            user.status = UserStatus.INACTIVE
            deactivated_count += 1
            deactivated_users.append({
                "id": user.id,
                "name": user.name,
                "phone": user.phone,
                "subscription_end_date": user.subscription_end_date.isoformat()
            })
            logger.info(f"Deactivated expired user: {user.name} (ID: {user.id})")
        
        db.commit()
        
        result = {
            "success": True,
            "message": f"Deactivated {deactivated_count} expired users",
            "deactivated_users": deactivated_users,
            "total_deactivated": deactivated_count,
            "check_date": today.isoformat()
        }
        
        logger.info(f"Subscription check completed: {result['message']}")
        return result
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error during subscription check: {str(e)}")
        return {
            "success": False,
            "message": f"Error during subscription check: {str(e)}",
            "total_deactivated": 0,
            "check_date": date.today().isoformat()
        }
    finally:
        db.close()

def get_users_expiring_soon(days: int = 7) -> dict:
    """
    Get users whose subscriptions are expiring within the specified number of days.
    """
    db = SessionLocal()
    try:
        today = date.today()
        future_date = today + timedelta(days=days)
        
        expiring_users = db.query(User).filter(
            User.status == UserStatus.ACTIVE,
            User.subscription_end_date.isnot(None),
            User.subscription_end_date >= today,
            User.subscription_end_date <= future_date,
            User.role != UserRole.ADMIN
        ).all()
        
        result = {
            "success": True,
            "message": f"Found {len(expiring_users)} users expiring within {days} days",
            "expiring_users": [
                {
                    "id": user.id,
                    "name": user.name,
                    "phone": user.phone,
                    "subscription_end_date": user.subscription_end_date.isoformat(),
                    "days_remaining": (user.subscription_end_date - today).days
                }
                for user in expiring_users
            ],
            "total_expiring": len(expiring_users),
            "check_date": today.isoformat()
        }
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting expiring users: {str(e)}")
        return {
            "success": False,
            "message": f"Error getting expiring users: {str(e)}",
            "total_expiring": 0,
            "check_date": date.today().isoformat()
        }
    finally:
        db.close()