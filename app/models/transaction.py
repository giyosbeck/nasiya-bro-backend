from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
from app.core.timezone import uzbekistan_now
import enum

class TransactionType(str, enum.Enum):
    SALE = "sale"
    LOAN = "loan"
    LOAN_PAYMENT = "loan_payment"
    PRODUCT_RESTOCK = "product_restock"
    REFUND = "refund"

class Sale(Base):
    __tablename__ = "sales"
    
    id = Column(Integer, primary_key=True, index=True)
    sale_price = Column(Float, nullable=False)
    sale_date = Column(DateTime(timezone=True), default=uzbekistan_now)
    imei = Column(String(20), nullable=True)
    created_at = Column(DateTime(timezone=True), default=uzbekistan_now)
    
    # Foreign keys
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    seller_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    magazine_id = Column(Integer, ForeignKey("magazines.id"), nullable=False)
    
    # Relationships
    product = relationship("Product", back_populates="sales")
    seller = relationship("User", back_populates="sales")
    magazine = relationship("Magazine", back_populates="sales")

class Loan(Base):
    __tablename__ = "loans"
    
    id = Column(Integer, primary_key=True, index=True)
    loan_price = Column(Float, nullable=False)
    initial_payment = Column(Float, nullable=False)
    remaining_amount = Column(Float, nullable=False)
    loan_months = Column(Integer, nullable=False)
    interest_rate = Column(Float, nullable=False)
    monthly_payment = Column(Float, nullable=False)
    loan_start_date = Column(DateTime(timezone=True), nullable=False)
    video_url = Column(String, nullable=True)
    agreement_images = Column(Text, nullable=True)  # JSON string of image URLs
    imei = Column(String(20), nullable=True)
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=uzbekistan_now)
    
    # Foreign keys
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    seller_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    magazine_id = Column(Integer, ForeignKey("magazines.id"), nullable=False)
    
    # Relationships
    product = relationship("Product", back_populates="loans")
    client = relationship("Client", back_populates="loans")
    seller = relationship("User", back_populates="loans")
    magazine = relationship("Magazine", back_populates="loans")
    payments = relationship("LoanPayment", back_populates="loan")

class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    OVERDUE = "overdue"

class LoanPayment(Base):
    __tablename__ = "loan_payments"
    
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    payment_date = Column(DateTime(timezone=True), nullable=True)  # Null until payment is made
    due_date = Column(DateTime(timezone=True), nullable=False)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    is_late = Column(Boolean, default=False)
    is_full_payment = Column(Boolean, default=False)  # True if this is a one-time full loan payment
    notes = Column(Text, nullable=True)  # Optional notes for payment (delays, reasons, etc.)
    created_at = Column(DateTime(timezone=True), default=uzbekistan_now)
    
    # Foreign key
    loan_id = Column(Integer, ForeignKey("loans.id"), nullable=False)
    
    # Relationship
    loan = relationship("Loan", back_populates="payments")

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    type = Column(Enum(TransactionType), nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=uzbekistan_now)
    
    # Foreign keys - nullable to handle different transaction types
    sale_id = Column(Integer, ForeignKey("sales.id"), nullable=True)
    loan_id = Column(Integer, ForeignKey("loans.id"), nullable=True)
    loan_payment_id = Column(Integer, ForeignKey("loan_payments.id"), nullable=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=True)
    seller_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    magazine_id = Column(Integer, ForeignKey("magazines.id"), nullable=False)
    
    # Relationships
    sale = relationship("Sale")
    loan = relationship("Loan")
    loan_payment = relationship("LoanPayment")
    product = relationship("Product")
    client = relationship("Client")
    seller = relationship("User")
    magazine = relationship("Magazine") 