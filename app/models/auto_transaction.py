from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
from app.core.timezone import uzbekistan_now
from app.models.transaction import PaymentStatus
import enum

class AutoSale(Base):
    __tablename__ = "auto_sales"
    
    id = Column(Integer, primary_key=True, index=True)
    sale_price = Column(Float, nullable=False)
    sale_date = Column(DateTime(timezone=True), default=uzbekistan_now)
    created_at = Column(DateTime(timezone=True), default=uzbekistan_now)
    
    # Foreign keys
    auto_product_id = Column(Integer, ForeignKey("auto_products.id"), nullable=False)
    seller_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    magazine_id = Column(Integer, ForeignKey("magazines.id"), nullable=False)
    
    # Relationships
    auto_product = relationship("AutoProduct", back_populates="auto_sales")
    seller = relationship("User")
    magazine = relationship("Magazine")

class AutoLoan(Base):
    __tablename__ = "auto_loans"
    
    id = Column(Integer, primary_key=True, index=True)
    loan_price = Column(Float, nullable=False)
    initial_payment = Column(Float, nullable=False)
    remaining_amount = Column(Float, nullable=False)
    loan_months = Column(Integer, nullable=False)
    yearly_interest_rate = Column(Float, nullable=False)  # Gadavoy foiz
    monthly_payment = Column(Float, nullable=False)
    loan_start_date = Column(DateTime(timezone=True), nullable=False)
    video_url = Column(String, nullable=True)  # Video uploading
    agreement_images = Column(Text, nullable=True)  # Shartnoma - JSON string of image URLs
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=uzbekistan_now)
    
    # Foreign keys
    auto_product_id = Column(Integer, ForeignKey("auto_products.id"), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    seller_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    magazine_id = Column(Integer, ForeignKey("magazines.id"), nullable=False)
    
    # Relationships
    auto_product = relationship("AutoProduct", back_populates="auto_loans")
    client = relationship("Client")
    seller = relationship("User")
    magazine = relationship("Magazine")
    payments = relationship("AutoLoanPayment", back_populates="auto_loan")

class AutoLoanPayment(Base):
    __tablename__ = "auto_loan_payments"
    
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    payment_date = Column(DateTime(timezone=True), nullable=True)  # Null until payment is made
    due_date = Column(DateTime(timezone=True), nullable=False)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    is_late = Column(Boolean, default=False)
    is_full_payment = Column(Boolean, default=False)  # True if this is a one-time full loan payment
    notes = Column(Text, nullable=True)  # Optional notes for payment
    created_at = Column(DateTime(timezone=True), default=uzbekistan_now)
    
    # Foreign key
    auto_loan_id = Column(Integer, ForeignKey("auto_loans.id"), nullable=False)
    
    # Relationship
    auto_loan = relationship("AutoLoan", back_populates="payments")