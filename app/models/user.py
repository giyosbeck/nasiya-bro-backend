from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
import enum

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    SELLER = "seller"

class UserStatus(str, enum.Enum):
    PENDING = "pending"
    ACTIVE = "active"
    INACTIVE = "inactive"

class UserType(str, enum.Enum):
    GADGETS = "gadgets"
    AUTO = "auto"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    status = Column(Enum(UserStatus), default=UserStatus.PENDING)
    user_type = Column(Enum(UserType), default=UserType.GADGETS)
    magazine_name = Column(String, nullable=True)
    subscription_end_date = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Reference to magazine (all users belong to a magazine)
    magazine_id = Column(Integer, ForeignKey("magazines.id"), nullable=True)
    
    # For sellers - reference to manager
    manager_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    magazine = relationship("Magazine", back_populates="users", foreign_keys=[magazine_id])
    manager = relationship("User", remote_side=[id], back_populates="sellers", foreign_keys=[manager_id])
    sellers = relationship("User", back_populates="manager", foreign_keys=[manager_id])
    sales = relationship("Sale", back_populates="seller")
    loans = relationship("Loan", back_populates="seller")

class Client(Base):
    __tablename__ = "clients"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    passport_series = Column(String, nullable=False, unique=True, index=True)
    passport_image_url = Column(String, nullable=True)  # Keep for backward compatibility
    passport_image_urls = Column(String, nullable=True)  # JSON array of all image paths
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship to manager who added this client
    manager_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    manager = relationship("User")
    
    # Relationships
    loans = relationship("Loan", back_populates="client") 