from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, validator
from app.models.notification import NotificationType, NotificationStatus, DeviceType

class PushTokenCreate(BaseModel):
    push_token: str
    device_type: DeviceType = DeviceType.mobile

class PushTokenResponse(BaseModel):
    id: int
    token: str
    user_id: int
    device_type: DeviceType
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class NotificationCreate(BaseModel):
    type: NotificationType
    title: str
    body: str
    data: Optional[Dict[str, Any]] = None
    recipient_user_id: Optional[int] = None
    recipient_role: Optional[str] = None

class NotificationResponse(BaseModel):
    id: int
    type: NotificationType
    title: str
    body: str
    data: Optional[Dict[str, Any]]
    recipient_user_id: Optional[int]
    recipient_role: Optional[str]
    sender_user_id: Optional[int]
    status: NotificationStatus
    sent_at: Optional[datetime]
    delivered_at: Optional[datetime]
    error_message: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class AdminAlertRequest(BaseModel):
    type: str  # Will be converted to NotificationType
    title: str
    body: str
    data: Optional[Dict[str, Any]] = None
    recipient_role: Optional[str] = "admin"  # "admin", "manager", or "all"
    
    @validator('type')
    def validate_type(cls, v):
        valid_types = [
            'new_user_registration',
            'payment_overdue', 
            'loan_approved',
            'loan_rejected'
        ]
        if v.lower() not in valid_types:
            raise ValueError(f'Invalid notification type. Must be one of: {valid_types}')
        return v.lower()

class UserRegistrationAlert(BaseModel):
    user_id: int
    user_name: str
    user_phone: str
    registration_date: str

class PaymentOverdueAlert(BaseModel):
    client_name: str
    amount: float
    days_past_due: int
    loan_id: int

class LoanStatusAlert(BaseModel):
    client_name: str
    loan_amount: float
    status: str  # "approved" or "rejected"
    loan_id: int

class NotificationPreferenceCreate(BaseModel):
    notification_type: NotificationType
    is_enabled: bool = True

class NotificationPreferenceResponse(BaseModel):
    id: int
    user_id: int
    notification_type: NotificationType
    is_enabled: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class NotificationStats(BaseModel):
    total_notifications: int
    unread_count: int
    notifications_by_type: Dict[str, int]
    recent_notifications: List[NotificationResponse]