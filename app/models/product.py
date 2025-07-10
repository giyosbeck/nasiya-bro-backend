from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    model = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Reference to manager who owns this warehouse
    manager_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    manager = relationship("User")
    
    # Relationships
    sales = relationship("Sale", back_populates="product")
    loans = relationship("Loan", back_populates="product") 