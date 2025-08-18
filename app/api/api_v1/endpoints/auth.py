from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User, UserRole, UserStatus
from app.models.magazine import Magazine
from app.schemas.user import UserCreate, UserLogin, Token, UserResponse
from app.core.security import verify_password, get_password_hash, create_access_token
from app.api.deps import get_current_user

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

@router.post("/register", response_model=Token)
def register_manager(
    user_data: UserCreate,
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
        status=UserStatus.PENDING
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Load magazine relationship for response
    if new_user.magazine:
        new_user.magazine_name = new_user.magazine.name
    
    # Generate access token for pending user (so they can stay logged in)
    access_token = create_access_token(subject=new_user.id)
    
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
    """Permanently delete user account"""
    try:
        # Delete the user account
        db.delete(current_user)
        db.commit()
        
        return {"message": "Account successfully deleted"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to delete account"
        ) 