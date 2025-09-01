from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
import enum

class NotificationType(str, enum.Enum):
    new_user_registration = "new_user_registration"
    payment_overdue = "payment_overdue"
    loan_approved = "loan_approved"
    loan_rejected = "loan_rejected"
    payment_reminder = "payment_reminder"

class NotificationStatus(str, enum.Enum):
    pending = "pending"
    sent = "sent"
    failed = "failed"
    delivered = "delivered"

class DeviceType(str, enum.Enum):
    mobile = "mobile"
    web = "web"

class PushToken(Base):
    __tablename__ = "push_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, nullable=False, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    device_type = Column(Enum(DeviceType), default=DeviceType.mobile)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User")

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    type = Column(Enum(NotificationType), nullable=False)
    title = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    data = Column(JSON, nullable=True)  # Additional data payload
    
    # Recipient information
    recipient_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    recipient_role = Column(String, nullable=True)  # For broadcasting to roles
    
    # Sender information
    sender_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Delivery information
    push_token_id = Column(Integer, ForeignKey("push_tokens.id"), nullable=True)
    status = Column(Enum(NotificationStatus), default=NotificationStatus.pending)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    recipient = relationship("User", foreign_keys=[recipient_user_id])
    sender = relationship("User", foreign_keys=[sender_user_id])
    push_token = relationship("PushToken")

class NotificationPreference(Base):
    __tablename__ = "notification_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    notification_type = Column(Enum(NotificationType), nullable=False)
    is_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User")