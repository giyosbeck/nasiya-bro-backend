from typing import List
from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User, UserRole, UserStatus
from app.schemas.user import UserResponse, SellerCreate, UserApproval, UserStatusUpdate
from app.api.deps import get_current_admin_user, get_current_manager_user
from app.core.security import get_password_hash

router = APIRouter()

@router.get("/", response_model=List[UserResponse])
def get_all_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get all users (admin only)"""
    users = db.query(User).all()
    return users

@router.get("/pending", response_model=List[UserResponse])
def get_pending_managers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get all pending manager approvals (admin only)"""
    pending_users = db.query(User).filter(
        User.role == UserRole.MANAGER,
        User.status == UserStatus.PENDING
    ).all()
    return pending_users

@router.put("/{user_id}/approve")
def approve_user(
    user_id: int,
    approval_data: UserApproval,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Approve a pending user with subscription (admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.status != UserStatus.PENDING:
        raise HTTPException(status_code=400, detail="User is not pending approval")
    
    # Calculate subscription end date
    today = date.today()
    subscription_end_date = today + timedelta(days=approval_data.subscription_months * 30)
    
    user.status = UserStatus.ACTIVE
    user.subscription_end_date = subscription_end_date
    db.commit()
    db.refresh(user)
    
    return {
        "message": f"User {user.name} has been approved",
        "subscription_end_date": subscription_end_date.isoformat(),
        "subscription_months": approval_data.subscription_months
    }

@router.put("/{user_id}/reject")
def reject_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Reject a pending user (admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.status != UserStatus.PENDING:
        raise HTTPException(status_code=400, detail="User is not pending approval")
    
    user.status = UserStatus.INACTIVE
    db.commit()
    db.refresh(user)
    
    return {"message": f"User {user.name} has been rejected"}

@router.get("/stats")
def get_user_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get user statistics (admin only)"""
    total_managers = db.query(User).filter(User.role == UserRole.MANAGER).count()
    pending_approvals = db.query(User).filter(
        User.role == UserRole.MANAGER,
        User.status == UserStatus.PENDING
    ).count()
    active_users = db.query(User).filter(User.status == UserStatus.ACTIVE).count()
    
    return {
        "total_managers": total_managers,
        "pending_approvals": pending_approvals,
        "active_users": active_users,
        "total_revenue": 0  # TODO: Calculate from sales/loans
    }

@router.put("/{user_id}/activate")
def activate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Activate an inactive user (admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.role == UserRole.ADMIN:
        raise HTTPException(status_code=400, detail="Cannot modify admin user status")
    
    if user.status == UserStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="User is already active")
    
    user.status = UserStatus.ACTIVE
    db.commit()
    db.refresh(user)
    
    return {"message": f"User {user.name} has been activated"}

@router.put("/{user_id}/deactivate")
def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Deactivate an active user (admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.role == UserRole.ADMIN:
        raise HTTPException(status_code=400, detail="Cannot deactivate admin user")
    
    if user.status != UserStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="User is not active")
    
    user.status = UserStatus.INACTIVE
    db.commit()
    db.refresh(user)
    
    return {"message": f"User {user.name} has been deactivated"}

@router.post("/sellers", response_model=UserResponse)
def create_seller(
    seller_data: SellerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_manager_user)
):
    """Create a new seller account (managers and admins only)"""
    # Check if phone number already exists
    existing_user = db.query(User).filter(User.phone == seller_data.phone).first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Phone number already registered"
        )
    
    # Create new seller linked to the current manager
    new_seller = User(
        name=seller_data.name,
        phone=seller_data.phone,
        password_hash=get_password_hash(seller_data.password),
        role=UserRole.SELLER,
        status=UserStatus.ACTIVE,  # Sellers are immediately active
        manager_id=current_user.id,  # Link to the manager who created this seller
        magazine_id=current_user.magazine_id  # Inherit magazine ID from manager
    )
    
    db.add(new_seller)
    db.commit()
    db.refresh(new_seller)
    
    return new_seller

@router.get("/sellers", response_model=List[UserResponse])
def get_my_sellers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_manager_user)
):
    """Get all sellers created by the current manager"""
    if current_user.role == UserRole.ADMIN:
        # Admins can see all sellers
        sellers = db.query(User).filter(User.role == UserRole.SELLER).all()
    else:
        # Managers can only see their own sellers
        sellers = db.query(User).filter(
            User.role == UserRole.SELLER,
            User.manager_id == current_user.id
        ).all()
    
    return sellers

@router.put("/sellers/{seller_id}/status")
def update_seller_status(
    seller_id: int,
    status_data: UserStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_manager_user)
):
    """Update a seller's status (managers can only update their own sellers)"""
    # Find the seller
    seller = db.query(User).filter(
        User.id == seller_id,
        User.role == UserRole.SELLER
    ).first()
    
    if not seller:
        raise HTTPException(
            status_code=404,
            detail="Seller not found"
        )
    
    # Check permission - managers can only update their own sellers, admins can update any
    if current_user.role == UserRole.MANAGER and seller.manager_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only update your own sellers"
        )
    
    # Prevent self-status change
    if seller.id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail="Cannot change your own status"
        )
    
    # Update the status
    old_status = seller.status
    seller.status = status_data.status
    db.commit()
    db.refresh(seller)
    
    return {
        "message": f"Seller {seller.name} status updated from {old_status.value} to {status_data.status.value}",
        "seller_id": seller.id,
        "seller_name": seller.name,
        "old_status": old_status.value,
        "new_status": status_data.status.value
    }

@router.post("/check-expired")
def check_and_deactivate_expired_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Check for expired subscriptions and deactivate users (admin only)"""
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
    
    db.commit()
    
    return {
        "message": f"Deactivated {deactivated_count} expired users",
        "deactivated_users": deactivated_users,
        "total_deactivated": deactivated_count
    }

@router.get("/expiring-soon")
def get_users_expiring_soon(
    days: int = 7,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get users whose subscriptions are expiring soon (admin only)"""
    today = date.today()
    future_date = today + timedelta(days=days)
    
    expiring_users = db.query(User).filter(
        User.status == UserStatus.ACTIVE,
        User.subscription_end_date.isnot(None),
        User.subscription_end_date >= today,
        User.subscription_end_date <= future_date,
        User.role != UserRole.ADMIN
    ).all()
    
    return {
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
        ]
    }

@router.put("/{user_id}/extend-subscription")
def extend_user_subscription(
    user_id: int,
    extension_data: UserApproval,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Extend a user's subscription (admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.role == UserRole.ADMIN:
        raise HTTPException(status_code=400, detail="Cannot modify admin user subscription")
    
    # Calculate new subscription end date
    if user.subscription_end_date and user.subscription_end_date > date.today():
        # Extend from current end date if still valid
        new_end_date = user.subscription_end_date + timedelta(days=extension_data.subscription_months * 30)
    else:
        # Start from today if expired or no previous subscription
        new_end_date = date.today() + timedelta(days=extension_data.subscription_months * 30)
    
    user.subscription_end_date = new_end_date
    
    # Reactivate user if they were inactive due to expiration
    if user.status == UserStatus.INACTIVE:
        user.status = UserStatus.ACTIVE
    
    db.commit()
    db.refresh(user)
    
    return {
        "message": f"Extended subscription for {user.name}",
        "new_subscription_end_date": new_end_date.isoformat(),
        "extension_months": extension_data.subscription_months,
        "user_status": user.status.value
    }

@router.post("/auto-check-expired")
def auto_check_expired_users(
    db: Session = Depends(get_db)
):
    """
    Automated endpoint to check for expired subscriptions.
    This endpoint can be called by cron jobs or external schedulers.
    No authentication required for automated systems.
    """
    from app.services.subscription_service import check_and_deactivate_expired_users
    
    result = check_and_deactivate_expired_users()
    
    if result["success"]:
        return result
    else:
        raise HTTPException(
            status_code=500,
            detail=result["message"]
        ) 