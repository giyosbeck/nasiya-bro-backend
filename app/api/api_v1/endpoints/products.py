from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models.product import Product
from app.models.user import User, UserRole
from app.api.deps import get_current_user
from pydantic import BaseModel

router = APIRouter()

class ProductCreate(BaseModel):
    name: str
    model: str
    price: float
    count: int = 0

class ProductUpdate(BaseModel):
    name: str = None
    model: str = None
    price: float = None
    count: int = None

class ProductResponse(BaseModel):
    id: int
    name: str
    model: str
    price: float
    count: int
    manager_id: int
    
    class Config:
        from_attributes = True

@router.get("/", response_model=List[ProductResponse])
def get_products(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all products for the current manager with pagination"""
    if current_user.role == UserRole.ADMIN:
        # Admin can see all products
        products = db.query(Product).offset(skip).limit(limit).all()
    else:
        # Managers and sellers can only see their manager's products
        manager_id = current_user.id if current_user.role == UserRole.MANAGER else current_user.manager_id
        products = db.query(Product).filter(Product.manager_id == manager_id).offset(skip).limit(limit).all()
    
    return products

@router.post("/", response_model=ProductResponse)
def create_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new product"""
    print(f"Product creation request from user: {current_user.name}, role: {current_user.role}, manager_id: {current_user.manager_id}")
    
    # Determine the manager ID
    if current_user.role == UserRole.ADMIN:
        # For admin, use their own ID as manager_id
        manager_id = current_user.id
    elif current_user.role == UserRole.MANAGER:
        # For managers, use their own ID
        manager_id = current_user.id
    else:
        # For sellers, use their manager's ID
        if not current_user.manager_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Seller account is not properly configured with a manager"
            )
        manager_id = current_user.manager_id
    
    print(f"Using manager_id: {manager_id} for product creation")
    
    new_product = Product(
        name=product_data.name,
        model=product_data.model,
        price=product_data.price,
        count=product_data.count,
        manager_id=manager_id
    )
    
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    
    return new_product

@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a product"""
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Check if user has permission to update this product
    if current_user.role == UserRole.ADMIN:
        # Admin can update any product
        pass
    elif current_user.role == UserRole.MANAGER:
        # Managers can only update their own products
        if product.manager_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own products"
            )
    else:
        # Sellers can only update stock count for their manager's products
        manager_id = current_user.manager_id
        if product.manager_id != manager_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update products from your manager's warehouse"
            )
        # Sellers can only update count field
        update_data = product_data.dict(exclude_unset=True)
        if any(field != 'count' for field in update_data.keys()):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sellers can only update product stock count"
            )
    
    # Update fields that are provided
    update_data = product_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)
    
    db.commit()
    db.refresh(product)
    
    return product

@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a product"""
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Check if user has permission to delete this product
    if current_user.role == UserRole.ADMIN:
        # Admin can delete any product
        pass
    elif current_user.role == UserRole.MANAGER:
        # Managers can only delete their own products
        if product.manager_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own products"
            )
    else:
        # Sellers cannot delete products
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete products"
        )
    
    db.delete(product)
    db.commit()
    
    return {"message": "Product deleted successfully"}

@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific product by ID"""
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Check if user has permission to view this product
    if current_user.role == UserRole.ADMIN:
        # Admin can view any product
        pass
    else:
        # Managers and sellers can only view their manager's products
        manager_id = current_user.id if current_user.role == UserRole.MANAGER else current_user.manager_id
        if product.manager_id != manager_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your own products"
            )
    
    return product 