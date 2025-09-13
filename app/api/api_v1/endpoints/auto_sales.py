from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from datetime import datetime
from app.db.database import get_db
from app.models.auto_transaction import AutoSale
from app.models.auto_product import AutoProduct
from app.models.user import User, UserRole
from app.api.deps import get_current_user
from app.core.timezone import to_uzbekistan_time
from pydantic import BaseModel

router = APIRouter()

class AutoSaleCreate(BaseModel):
    auto_product_id: int
    sale_price: float

class AutoSaleResponse(BaseModel):
    id: int
    sale_price: float
    sale_date: datetime
    created_at: datetime
    auto_product_id: int
    seller_id: int
    car_name: str
    model: str
    color: str
    year: int
    seller_name: str
    
    class Config:
        from_attributes = True

@router.get("/", response_model=List[AutoSaleResponse])
def get_auto_sales(
    limit: int = 10,
    offset: int = 0,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all auto sales for the current user's scope with filtering support"""
    query = db.query(AutoSale).join(AutoProduct).join(User)
    
    # Apply user scope filtering
    if current_user.role == UserRole.MANAGER:
        query = query.filter(AutoSale.seller_id == current_user.id)
    elif current_user.role == UserRole.OWNER:
        query = query.filter(AutoSale.magazine_id == current_user.magazine_id)
    
    # Apply date filtering
    if date_from:
        try:
            from_date = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
            query = query.filter(AutoSale.sale_date >= from_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date_from format")
    
    if date_to:
        try:
            to_date = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
            query = query.filter(AutoSale.sale_date <= to_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date_to format")
    
    # Apply search filtering
    if search:
        query = query.filter(
            or_(
                AutoProduct.car_name.ilike(f"%{search}%"),
                AutoProduct.model.ilike(f"%{search}%"),
                AutoProduct.color.ilike(f"%{search}%"),
                User.name.ilike(f"%{search}%")
            )
        )
    
    # Get total count for pagination
    total = query.count()
    
    # Apply pagination
    auto_sales = query.offset(offset).limit(limit).all()
    
    # Transform to response format
    result = []
    for sale in auto_sales:
        sale_data = AutoSaleResponse(
            id=sale.id,
            sale_price=sale.sale_price,
            sale_date=to_uzbekistan_time(sale.sale_date),
            created_at=to_uzbekistan_time(sale.created_at),
            auto_product_id=sale.auto_product_id,
            seller_id=sale.seller_id,
            car_name=sale.auto_product.car_name,
            model=sale.auto_product.model,
            color=sale.auto_product.color,
            year=sale.auto_product.year,
            seller_name=sale.seller.name
        )
        result.append(sale_data)
    
    return result

@router.post("/", response_model=AutoSaleResponse)
def create_auto_sale(
    sale: AutoSaleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new auto sale"""
    
    # Verify auto product exists and user has access
    auto_product = db.query(AutoProduct).filter(AutoProduct.id == sale.auto_product_id).first()
    if not auto_product:
        raise HTTPException(status_code=404, detail="Auto product not found")
    
    # Check if user has permission to sell this auto product
    if current_user.role == UserRole.MANAGER:
        if auto_product.manager_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to sell this auto product")
    elif current_user.role == UserRole.OWNER:
        if auto_product.magazine_id != current_user.magazine_id:
            raise HTTPException(status_code=403, detail="Not authorized to sell this auto product")
    
    # Check if auto product is in stock
    if auto_product.count <= 0:
        raise HTTPException(status_code=400, detail="Auto product is out of stock")
    
    # Create the auto sale
    db_auto_sale = AutoSale(
        auto_product_id=sale.auto_product_id,
        sale_price=sale.sale_price,
        seller_id=current_user.id
    )
    
    db.add(db_auto_sale)
    
    # Decrease auto product count
    auto_product.count -= 1
    
    db.commit()
    db.refresh(db_auto_sale)
    
    return AutoSaleResponse(
        id=db_auto_sale.id,
        sale_price=db_auto_sale.sale_price,
        sale_date=to_uzbekistan_time(db_auto_sale.sale_date),
        created_at=to_uzbekistan_time(db_auto_sale.created_at),
        auto_product_id=db_auto_sale.auto_product_id,
        seller_id=db_auto_sale.seller_id,
        car_name=auto_product.car_name,
        model=auto_product.model,
        color=auto_product.color,
        year=auto_product.year,
        seller_name=current_user.name
    )

@router.get("/{sale_id}", response_model=AutoSaleResponse)
def get_auto_sale(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific auto sale by ID"""
    
    query = db.query(AutoSale).join(AutoProduct).join(User).filter(AutoSale.id == sale_id)
    
    # Apply user scope filtering
    if current_user.role == UserRole.MANAGER:
        query = query.filter(AutoSale.seller_id == current_user.id)
    elif current_user.role == UserRole.OWNER:
        query = query.filter(AutoSale.magazine_id == current_user.magazine_id)
    
    auto_sale = query.first()
    if not auto_sale:
        raise HTTPException(status_code=404, detail="Auto sale not found")
    
    return AutoSaleResponse(
        id=auto_sale.id,
        sale_price=auto_sale.sale_price,
        sale_date=to_uzbekistan_time(auto_sale.sale_date),
        created_at=to_uzbekistan_time(auto_sale.created_at),
        auto_product_id=auto_sale.auto_product_id,
        seller_id=auto_sale.seller_id,
        car_name=auto_sale.auto_product.car_name,
        model=auto_sale.auto_product.model,
        color=auto_sale.auto_product.color,
        year=auto_sale.auto_product.year,
        seller_name=auto_sale.seller.name
    )