from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import date, timedelta
from pydantic import BaseModel

from app.api import deps
from app.models.user import User, UserRole, UserStatus
from app.models.magazine import Magazine, MagazineStatus
from app.db.database import get_db

class SubscriptionRequest(BaseModel):
    subscription_months: int

router = APIRouter()

@router.get("/", response_model=List[dict])
def get_all_magazines(
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(get_db)
):
    """Get all magazines (admin only)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    magazines = db.query(Magazine).all()
    
    result = []
    for mag in magazines:
        # Get the manager for this magazine
        manager = db.query(User).filter(
            User.magazine_id == mag.id,
            User.role == UserRole.MANAGER
        ).first()
        
        result.append({
            "id": mag.id,
            "name": mag.name,
            "status": mag.status.value,
            "subscription_end_date": mag.subscription_end_date,
            "created_at": mag.created_at,
            "manager": {
                "id": manager.id if manager else None,
                "name": manager.name if manager else "No Manager",
                "phone": manager.phone if manager else "",
                "status": manager.status.value if manager else "inactive"
            } if manager else None
        })
    
    return result

@router.get("/pending")
def get_pending_magazines(
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(get_db)
):
    """Get pending magazines awaiting approval"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    magazines = db.query(Magazine).filter(
        Magazine.status == MagazineStatus.PENDING
    ).all()
    
    result = []
    for mag in magazines:
        manager = db.query(User).filter(
            User.magazine_id == mag.id,
            User.role == UserRole.MANAGER
        ).first()
        
        result.append({
            "id": mag.id,
            "name": mag.name,
            "status": mag.status.value,
            "subscription_end_date": mag.subscription_end_date,
            "created_at": mag.created_at,
            "manager": {
                "id": manager.id if manager else None,
                "name": manager.name if manager else "No Manager",
                "phone": manager.phone if manager else "",
                "status": manager.status.value if manager else "inactive"
            } if manager else None
        })
    
    return result

@router.get("/expiring-soon")
def get_expiring_magazines(
    days: int = 30,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(get_db)
):
    """Get magazines expiring within specified days"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    cutoff_date = date.today() + timedelta(days=days)
    
    magazines = db.query(Magazine).filter(
        and_(
            Magazine.status == MagazineStatus.ACTIVE,
            Magazine.subscription_end_date <= cutoff_date,
            Magazine.subscription_end_date >= date.today()
        )
    ).all()
    
    result = []
    for mag in magazines:
        manager = db.query(User).filter(
            User.magazine_id == mag.id,
            User.role == UserRole.MANAGER
        ).first()
        
        result.append({
            "id": mag.id,
            "name": mag.name,
            "status": mag.status.value,
            "subscription_end_date": mag.subscription_end_date,
            "created_at": mag.created_at,
            "manager": {
                "id": manager.id if manager else None,
                "name": manager.name if manager else "No Manager",
                "phone": manager.phone if manager else "",
                "status": manager.status.value if manager else "inactive"
            } if manager else None
        })
    
    return result


@router.get("/inactive")
def get_inactive_magazines(
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(get_db)
):
    """Get all inactive magazines"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    magazines = db.query(Magazine).filter(
        Magazine.status == MagazineStatus.INACTIVE
    ).all()
    
    result = []
    for mag in magazines:
        manager = db.query(User).filter(
            User.magazine_id == mag.id,
            User.role == UserRole.MANAGER
        ).first()
        
        result.append({
            "id": mag.id,
            "name": mag.name,
            "status": mag.status.value,
            "subscription_end_date": mag.subscription_end_date,
            "created_at": mag.created_at,
            "manager": {
                "id": manager.id if manager else None,
                "name": manager.name if manager else "No Manager",
                "phone": manager.phone if manager else "",
                "status": manager.status.value if manager else "inactive"
            } if manager else None
        })
    
    return result


@router.put("/{magazine_id}/approve")
def approve_magazine(
    magazine_id: int,
    request: SubscriptionRequest,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(get_db)
):
    """Approve a magazine with subscription duration"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    magazine = db.query(Magazine).filter(Magazine.id == magazine_id).first()
    if not magazine:
        raise HTTPException(status_code=404, detail="Magazine not found")
    
    # Update magazine status and subscription
    magazine.status = MagazineStatus.ACTIVE
    magazine.subscription_end_date = date.today() + timedelta(days=30 * request.subscription_months)
    magazine.approved_by = current_user.id
    
    # Also update the manager's status
    manager = db.query(User).filter(
        User.magazine_id == magazine_id,
        User.role == UserRole.MANAGER
    ).first()
    
    if manager:
        manager.status = UserStatus.ACTIVE
        manager.subscription_end_date = magazine.subscription_end_date
    
    db.commit()
    
    return {"message": f"Magazine approved with {request.subscription_months} months subscription"}

@router.put("/{magazine_id}/reject")
def reject_magazine(
    magazine_id: int,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(get_db)
):
    """Reject a magazine registration"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    magazine = db.query(Magazine).filter(Magazine.id == magazine_id).first()
    if not magazine:
        raise HTTPException(status_code=404, detail="Magazine not found")
    
    # Update magazine status
    magazine.status = MagazineStatus.INACTIVE
    
    # Also update the manager's status
    manager = db.query(User).filter(
        User.magazine_id == magazine_id,
        User.role == UserRole.MANAGER
    ).first()
    
    if manager:
        manager.status = UserStatus.INACTIVE
    
    db.commit()
    
    return {"message": "Magazine registration rejected"}

@router.put("/{magazine_id}/activate")
def activate_magazine(
    magazine_id: int,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(get_db)
):
    """Activate a magazine"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    magazine = db.query(Magazine).filter(Magazine.id == magazine_id).first()
    if not magazine:
        raise HTTPException(status_code=404, detail="Magazine not found")
    
    magazine.status = MagazineStatus.ACTIVE
    
    # Also update the manager's status
    manager = db.query(User).filter(
        User.magazine_id == magazine_id,
        User.role == UserRole.MANAGER
    ).first()
    
    if manager:
        manager.status = UserStatus.ACTIVE
    
    db.commit()
    
    return {"message": "Magazine activated"}

@router.put("/{magazine_id}/deactivate")
def deactivate_magazine(
    magazine_id: int,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(get_db)
):
    """Deactivate a magazine"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    magazine = db.query(Magazine).filter(Magazine.id == magazine_id).first()
    if not magazine:
        raise HTTPException(status_code=404, detail="Magazine not found")
    
    magazine.status = MagazineStatus.INACTIVE
    
    # Also update the manager's status  
    manager = db.query(User).filter(
        User.magazine_id == magazine_id,
        User.role == UserRole.MANAGER
    ).first()
    
    if manager:
        manager.status = UserStatus.INACTIVE
    
    db.commit()
    
    return {"message": "Magazine deactivated"}

@router.put("/{magazine_id}/extend-subscription")
def extend_magazine_subscription(
    magazine_id: int,
    request: SubscriptionRequest,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(get_db)
):
    """Extend magazine subscription"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    magazine = db.query(Magazine).filter(Magazine.id == magazine_id).first()
    if not magazine:
        raise HTTPException(status_code=404, detail="Magazine not found")
    
    # Extend subscription from current end date or today, whichever is later
    current_end = magazine.subscription_end_date or date.today()
    start_date = max(current_end, date.today())
    new_end_date = start_date + timedelta(days=30 * request.subscription_months)
    
    magazine.subscription_end_date = new_end_date
    
    # Also update the manager's subscription
    manager = db.query(User).filter(
        User.magazine_id == magazine_id,
        User.role == UserRole.MANAGER
    ).first()
    
    if manager:
        manager.subscription_end_date = new_end_date
    
    db.commit()
    
    return {"message": f"Magazine subscription extended by {request.subscription_months} months"}

@router.get("/scheduler/status")
def get_scheduler_status(
    current_user: User = Depends(deps.get_current_user)
):
    """Get scheduler status and job information"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    from app.core.scheduler import app_scheduler
    
    return {
        "status": "active",
        "jobs": app_scheduler.get_jobs(),
        "message": "Automated expiration checks are running daily at 2:00 AM (magazines) and 2:30 AM (users)"
    }