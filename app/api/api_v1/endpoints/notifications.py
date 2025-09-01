from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import datetime

from app.db.database import get_db
from app.api.deps import get_current_user
from app.models.user import User, UserRole
from app.models.notification import PushToken, Notification, NotificationPreference, NotificationType, NotificationStatus, DeviceType
from app.schemas.notification import (
    PushTokenCreate, PushTokenResponse, NotificationCreate, NotificationResponse, 
    AdminAlertRequest, NotificationPreferenceCreate, NotificationPreferenceResponse
)
from app.services.notification_service import NotificationService

router = APIRouter()
notification_service = NotificationService()

@router.post("/register-token", response_model=dict)
async def register_push_token(
    token_data: PushTokenCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Register or update push token for current user"""
    try:
        # Check if token already exists for this user
        existing_token = db.query(PushToken).filter(
            and_(
                PushToken.user_id == current_user.id,
                PushToken.device_type == token_data.device_type
            )
        ).first()
        
        if existing_token:
            # Update existing token
            existing_token.token = token_data.push_token
            existing_token.is_active = True
            existing_token.updated_at = datetime.now()
        else:
            # Create new token
            new_token = PushToken(
                token=token_data.push_token,
                user_id=current_user.id,
                device_type=token_data.device_type
            )
            db.add(new_token)
        
        db.commit()
        
        return {
            "success": True,
            "message": "Push token registered successfully",
            "user_id": current_user.id,
            "device_type": token_data.device_type
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to register push token: {str(e)}"
        )

@router.post("/register-admin-token", response_model=dict)
async def register_admin_push_token(
    token_data: PushTokenCreate,
    admin_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Register push token for admin user (admin only)"""
    # Verify current user is admin
    if current_user.role not in [UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can register admin tokens"
        )
    
    try:
        # Get admin user
        admin_user = db.query(User).filter(
            and_(User.id == admin_id, User.role == UserRole.ADMIN)
        ).first()
        
        if not admin_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Admin user not found"
            )
        
        # Check if token already exists
        existing_token = db.query(PushToken).filter(
            and_(
                PushToken.user_id == admin_id,
                PushToken.device_type == token_data.device_type
            )
        ).first()
        
        if existing_token:
            existing_token.token = token_data.push_token
            existing_token.is_active = True
            existing_token.updated_at = datetime.now()
        else:
            new_token = PushToken(
                token=token_data.push_token,
                user_id=admin_id,
                device_type=token_data.device_type
            )
            db.add(new_token)
        
        db.commit()
        
        return {
            "success": True,
            "message": "Admin push token registered successfully",
            "admin_id": admin_id
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to register admin token: {str(e)}"
        )

@router.post("/admin-alert", response_model=dict)
async def send_admin_alert(
    alert_request: AdminAlertRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send alert notification to admins"""
    try:
        # Determine recipient admins based on role filter
        if alert_request.recipient_role == "admin":
            recipients = db.query(User).filter(User.role == UserRole.ADMIN).all()
        elif alert_request.recipient_role == "manager":
            recipients = db.query(User).filter(User.role == UserRole.MANAGER).all()
        else:  # "all"
            recipients = db.query(User).filter(
                User.role.in_([UserRole.ADMIN, UserRole.MANAGER])
            ).all()
        
        notifications_sent = 0
        
        for recipient in recipients:
            # Get active push tokens for recipient
            push_tokens = db.query(PushToken).filter(
                and_(
                    PushToken.user_id == recipient.id,
                    PushToken.is_active == True
                )
            ).all()
            
            for token in push_tokens:
                # Create notification record
                notification = Notification(
                    type=getattr(NotificationType, alert_request.type),
                    title=alert_request.title,
                    body=alert_request.body,
                    data=alert_request.data,
                    recipient_user_id=recipient.id,
                    sender_user_id=current_user.id,
                    push_token_id=token.id,
                    status=NotificationStatus.pending
                )
                db.add(notification)
                db.commit()
                
                # Send notification in background
                background_tasks.add_task(
                    notification_service.send_push_notification,
                    token.token,
                    alert_request.title,
                    alert_request.body,
                    alert_request.data,
                    notification.id,
                    db
                )
                notifications_sent += 1
        
        return {
            "success": True,
            "message": f"Admin alert queued for {notifications_sent} devices",
            "recipients_count": len(recipients),
            "notifications_sent": notifications_sent
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send admin alert: {str(e)}"
        )

@router.get("/my-notifications", response_model=List[NotificationResponse])
async def get_my_notifications(
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get notifications for current user"""
    notifications = db.query(Notification).filter(
        Notification.recipient_user_id == current_user.id
    ).order_by(Notification.created_at.desc()).offset(offset).limit(limit).all()
    
    return notifications

@router.put("/notifications/{notification_id}/mark-read", response_model=dict)
async def mark_notification_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark notification as read"""
    notification = db.query(Notification).filter(
        and_(
            Notification.id == notification_id,
            Notification.recipient_user_id == current_user.id
        )
    ).first()
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    notification.delivered_at = datetime.now()
    db.commit()
    
    return {"success": True, "message": "Notification marked as read"}

@router.get("/preferences", response_model=List[NotificationPreferenceResponse])
async def get_notification_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get notification preferences for current user"""
    preferences = db.query(NotificationPreference).filter(
        NotificationPreference.user_id == current_user.id
    ).all()
    
    return preferences

@router.post("/preferences", response_model=dict)
async def update_notification_preferences(
    preferences: List[NotificationPreferenceCreate],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update notification preferences for current user"""
    try:
        for pref_data in preferences:
            existing_pref = db.query(NotificationPreference).filter(
                and_(
                    NotificationPreference.user_id == current_user.id,
                    NotificationPreference.notification_type == pref_data.notification_type
                )
            ).first()
            
            if existing_pref:
                existing_pref.is_enabled = pref_data.is_enabled
                existing_pref.updated_at = datetime.now()
            else:
                new_pref = NotificationPreference(
                    user_id=current_user.id,
                    notification_type=pref_data.notification_type,
                    is_enabled=pref_data.is_enabled
                )
                db.add(new_pref)
        
        db.commit()
        
        return {
            "success": True,
            "message": "Notification preferences updated successfully"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update preferences: {str(e)}"
        )