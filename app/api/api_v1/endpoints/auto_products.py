from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models.user import User, UserType
from app.models.auto_product import AutoProduct
from app.api.deps import get_current_user
from pydantic import BaseModel

router = APIRouter()

class AutoProductCreate(BaseModel):
    car_name: str
    model: str
    color: str
    year: int
    purchase_price: float
    sale_price: float
    count: int = 1

class AutoProductUpdate(BaseModel):
    car_name: str = None
    model: str = None
    color: str = None
    year: int = None
    purchase_price: float = None
    sale_price: float = None
    count: int = None

class AutoProductResponse(BaseModel):
    id: int
    car_name: str
    model: str
    color: str
    year: int
    purchase_price: float
    sale_price: float
    count: int
    manager_id: int
    
    class Config:
        from_attributes = True

@router.get("/", response_model=List[AutoProductResponse])
def get_auto_products(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all auto products for the current user"""
    # Only allow auto users to access auto products
    if current_user.user_type != UserType.AUTO:
        raise HTTPException(
            status_code=403,
            detail="Only auto users can access auto products"
        )
    
    products = db.query(AutoProduct).filter(
        AutoProduct.manager_id == current_user.id
    ).all()
    
    return products

@router.post("/", response_model=AutoProductResponse)
def create_auto_product(
    product_data: AutoProductCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new auto product"""
    # Only allow auto users to create auto products
    if current_user.user_type != UserType.AUTO:
        raise HTTPException(
            status_code=403,
            detail="Only auto users can create auto products"
        )
    
    new_product = AutoProduct(
        car_name=product_data.car_name,
        model=product_data.model,
        color=product_data.color,
        year=product_data.year,
        purchase_price=product_data.purchase_price,
        sale_price=product_data.sale_price,
        count=product_data.count,
        manager_id=current_user.id
    )
    
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    
    return new_product

@router.get("/{product_id}", response_model=AutoProductResponse)
def get_auto_product(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific auto product"""
    if current_user.user_type != UserType.AUTO:
        raise HTTPException(
            status_code=403,
            detail="Only auto users can access auto products"
        )
    
    product = db.query(AutoProduct).filter(
        AutoProduct.id == product_id,
        AutoProduct.manager_id == current_user.id
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=404,
            detail="Auto product not found"
        )
    
    return product

@router.put("/{product_id}", response_model=AutoProductResponse)
def update_auto_product(
    product_id: int,
    product_data: AutoProductUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an auto product"""
    if current_user.user_type != UserType.AUTO:
        raise HTTPException(
            status_code=403,
            detail="Only auto users can update auto products"
        )
    
    product = db.query(AutoProduct).filter(
        AutoProduct.id == product_id,
        AutoProduct.manager_id == current_user.id
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=404,
            detail="Auto product not found"
        )
    
    # Update fields if provided
    for field, value in product_data.dict(exclude_unset=True).items():
        setattr(product, field, value)
    
    db.commit()
    db.refresh(product)
    
    return product

@router.delete("/{product_id}")
def delete_auto_product(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an auto product"""
    if current_user.user_type != UserType.AUTO:
        raise HTTPException(
            status_code=403,
            detail="Only auto users can delete auto products"
        )
    
    product = db.query(AutoProduct).filter(
        AutoProduct.id == product_id,
        AutoProduct.manager_id == current_user.id
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=404,
            detail="Auto product not found"
        )
    
    db.delete(product)
    db.commit()
    
    return {"message": "Auto product deleted successfully"}