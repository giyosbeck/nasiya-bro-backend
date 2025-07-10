from sqlalchemy import Column, Integer, String, DateTime, Text, Enum, Date, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
import enum

class MagazineStatus(str, enum.Enum):
    PENDING = "pending"
    ACTIVE = "active"
    INACTIVE = "inactive"

class Magazine(Base):
    __tablename__ = "magazines"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    address = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    status = Column(Enum(MagazineStatus), default=MagazineStatus.PENDING)
    subscription_end_date = Column(Date, nullable=True)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    users = relationship("User", back_populates="magazine", foreign_keys="User.magazine_id")
    sales = relationship("Sale", back_populates="magazine")
    loans = relationship("Loan", back_populates="magazine")
    approver = relationship("User", foreign_keys=[approved_by])