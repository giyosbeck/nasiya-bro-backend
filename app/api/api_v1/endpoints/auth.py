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

@router.post("/register", response_model=UserResponse)
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
    
    return new_user

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