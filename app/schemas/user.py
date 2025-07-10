from typing import Optional
from datetime import date
from pydantic import BaseModel, validator
from app.models.user import UserRole, UserStatus

class UserBase(BaseModel):
    name: str
    phone: str

class UserCreate(UserBase):
    password: str
    magazine_name: Optional[str] = None
    
    @validator('phone')
    def validate_phone(cls, v):
        if not v.startswith('+998'):
            raise ValueError('Phone number must start with +998')
        return v

class UserLogin(BaseModel):
    phone: str
    password: str

class UserResponse(UserBase):
    id: int
    role: UserRole
    status: UserStatus
    subscription_end_date: Optional[date] = None
    magazine_id: Optional[int] = None
    magazine_name: Optional[str] = None  # Will be populated from magazine relationship
    
    class Config:
        from_attributes = True

class SellerCreate(BaseModel):
    name: str
    phone: str
    password: str
    
    @validator('phone')
    def validate_phone(cls, v):
        if not v.startswith('+998'):
            raise ValueError('Phone number must start with +998')
        return v

class UserApproval(BaseModel):
    subscription_months: int
    
    @validator('subscription_months')
    def validate_subscription_months(cls, v):
        if v < 1 or v > 120:
            raise ValueError('Subscription months must be between 1 and 120')
        return v

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse 