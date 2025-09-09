from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

class AutoProduct(Base):
    __tablename__ = "auto_products"
    
    id = Column(Integer, primary_key=True, index=True)
    car_name = Column(String, nullable=False, index=True)  # Moshina nomi
    model = Column(String, nullable=False)  # Car model
    color = Column(String, nullable=False)  # Rangi
    year = Column(Integer, nullable=False)  # Yili
    purchase_price = Column(Float, nullable=False)  # Tan narxi
    sale_price = Column(Float, nullable=False)  # Sotuv narxi
    count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Reference to manager who owns this warehouse
    manager_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    manager = relationship("User")
    
    # Relationships
    auto_sales = relationship("AutoSale", back_populates="auto_product")
    auto_loans = relationship("AutoLoan", back_populates="auto_product")