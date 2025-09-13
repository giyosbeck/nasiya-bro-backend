from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User, UserRole, UserStatus, UserType
from app.models.magazine import Magazine
from app.schemas.user import UserCreate, UserLogin, Token, UserResponse
from app.core.security import verify_password, get_password_hash, create_access_token
from app.api.deps import get_current_user
from app.services.notification_service import NotificationService
from app.models.notification import PushToken, Notification, NotificationStatus, NotificationType

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

@router.post("/register", response_model=Token)
async def register_manager(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Register a new manager account"""
    # Check if user already exists
    existing_user = db.query(User).filter(User.phone == user_data.phone).first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Phone number already registered"
        )
    
    # Handle magazine creation/assignment
    magazine_id = None
    if user_data.magazine_name:
        # Try to find existing magazine first
        magazine = db.query(Magazine).filter(Magazine.name == user_data.magazine_name).first()
        
        if not magazine:
            # Create new magazine
            magazine = Magazine(name=user_data.magazine_name)
            db.add(magazine)
            db.flush()  # Flush to get the ID without committing
        
        magazine_id = magazine.id
    
    # Create new manager (status will be PENDING by default)
    new_user = User(
        name=user_data.name,
        phone=user_data.phone,
        password_hash=get_password_hash(user_data.password),
        role=UserRole.MANAGER,
        magazine_id=magazine_id,
        status=UserStatus.PENDING,
        user_type=user_data.user_type
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Load magazine relationship for response
    if new_user.magazine:
        new_user.magazine_name = new_user.magazine.name
    
    # Generate access token for pending user (so they can stay logged in)
    access_token = create_access_token(subject=new_user.id)
    
    # Send admin notification about new user registration
    try:
        # Get all admin users
        admins = db.query(User).filter(User.role == UserRole.ADMIN).all()
        
        for admin in admins:
            # Get active push tokens for admin
            push_tokens = db.query(PushToken).filter(
                PushToken.user_id == admin.id,
                PushToken.is_active == True
            ).all()
            
            for token in push_tokens:
                # Create notification record
                user_type_display = "Auto" if new_user.user_type == UserType.AUTO else ("Gadgets" if new_user.user_type == UserType.GADGETS else "Pending Mode Selection")
                notification = Notification(
                    type=NotificationType.new_user_registration,
                    title="New User Registration",
                    body=f"{new_user.name} ({user_type_display}) has registered and needs approval",
                    data={
                        "userId": str(new_user.id),
                        "userName": new_user.name,
                        "userPhone": new_user.phone,
                        "userType": new_user.user_type.value if new_user.user_type else None,
                        "registrationDate": new_user.created_at.isoformat() if new_user.created_at else None,
                        "magazineName": user_data.magazine_name
                    },
                    recipient_user_id=admin.id,
                    push_token_id=token.id,
                    status=NotificationStatus.pending
                )
                db.add(notification)
                
                # Send notification in background
                background_tasks.add_task(
                    NotificationService().send_push_notification,
                    token.token,
                    notification.title,
                    notification.body,
                    notification.data,
                    notification.id,
                    db
                )
        
        db.commit()
        print(f"✅ Admin notifications queued for new user registration: {new_user.name}")
        
    except Exception as e:
        print(f"⚠️  Failed to send admin notifications: {str(e)}")
        # Don't fail the registration if notification fails
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": new_user
    }

@router.post("/login", response_model=Token)
def login_form(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """OAuth2 compatible login endpoint (form data)"""
    user = db.query(User).filter(User.phone == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect phone number or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Admins are always allowed to login, others need ACTIVE status
    if user.role != UserRole.ADMIN and user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is pending approval or inactive"
        )
    
    access_token = create_access_token(subject=user.id)
    
    # Load magazine relationship for response
    if user.magazine:
        user.magazine_name = user.magazine.name
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@router.post("/login-json", response_model=Token)
def login_json(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """JSON-based login endpoint for mobile app"""
    user = db.query(User).filter(User.phone == login_data.phone).first()
    
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect phone number or password",
        )
    
    if user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is pending approval or inactive"
        )
    
    access_token = create_access_token(subject=user.id)
    
    # Load magazine relationship for response
    if user.magazine:
        user.magazine_name = user.magazine.name
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information"""
    # Load magazine relationship for response
    if current_user.magazine:
        current_user.magazine_name = current_user.magazine.name
    
    return current_user

@router.post("/logout")
def logout():
    """Logout endpoint (token should be removed on client side)"""
    return {"message": "Successfully logged out"}

@router.post("/check-approval-status")
def check_approval_status(
    request_data: dict,
    db: Session = Depends(get_db)
):
    """Check if user is approved without requiring authentication"""
    phone = request_data.get("phone")
    if not phone:
        raise HTTPException(
            status_code=400,
            detail="Phone number is required"
        )
    
    user = db.query(User).filter(User.phone == phone).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    # Load magazine relationship
    if user.magazine:
        user.magazine_name = user.magazine.name
    
    # If user is active, generate a token for them
    response_data = {
        "id": user.id,
        "name": user.name,
        "phone": user.phone,
        "role": user.role,
        "status": user.status,
        "magazine_id": user.magazine_id,
        "magazine_name": getattr(user, 'magazine_name', None)
    }
    
    # If user is active, include access token
    if user.status == UserStatus.ACTIVE:
        access_token = create_access_token(subject=user.id)
        response_data["access_token"] = access_token
        response_data["token_type"] = "bearer"
    
    return response_data

@router.delete("/delete-account")
def delete_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Deactivate user account (visually appears as deletion to user)"""
    # Prevent admins from deleting their accounts
    if current_user.role == UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin accounts cannot be deleted"
        )
    
    try:
        # Instead of deleting, mark the account as INACTIVE
        # This preserves data integrity while giving the user the experience of account deletion
        current_user.status = UserStatus.INACTIVE
        db.commit()
        
        return {"message": "Account successfully deleted"}
    except Exception as e:
        db.rollback()
        print(f"Error deactivating account: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to delete account"
        )

@router.put("/update-user-type")
def update_user_type(
    request_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user type (gadgets/auto)"""
    user_type_str = request_data.get("user_type")
    if not user_type_str:
        raise HTTPException(
            status_code=400,
            detail="User type is required"
        )
    
    # Validate user type
    if user_type_str not in ["gadgets", "auto"]:
        raise HTTPException(
            status_code=400,
            detail="User type must be either 'gadgets' or 'auto'"
        )
    
    user_type = UserType.GADGETS if user_type_str == "gadgets" else UserType.AUTO
    
    try:
        # Update user type
        current_user.user_type = user_type
        db.commit()
        
        # Return updated user data
        return {
            "message": "User type updated successfully",
            "user": {
                "id": current_user.id,
                "name": current_user.name,
                "phone": current_user.phone,
                "role": current_user.role,
                "status": current_user.status,
                "user_type": current_user.user_type,
                "magazine_id": current_user.magazine_id
            }
        }
    except Exception as e:
        db.rollback()
        print(f"Error updating user type: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to update user type"
        ) 