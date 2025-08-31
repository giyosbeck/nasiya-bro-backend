from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from datetime import datetime
from app.db.database import get_db
from app.models.transaction import Sale, TransactionType
from app.models.product import Product
from app.models.user import User, UserRole
from app.api.deps import get_current_user
from app.api.api_v1.endpoints.transactions import create_transaction
from app.core.timezone import to_uzbekistan_time
from pydantic import BaseModel

router = APIRouter()

class SaleCreate(BaseModel):
    product_id: int
    sale_price: float
    imei: Optional[str] = None

class SaleResponse(BaseModel):
    id: int
    sale_price: float
    sale_date: datetime
    created_at: datetime
    product_id: int
    seller_id: int
    product_name: str
    product_model: str
    seller_name: str
    imei: Optional[str]
    
    class Config:
        from_attributes = True

@router.get("/", response_model=List[SaleResponse])
def get_sales(
    limit: int = 10,
    offset: int = 0,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all sales for the current user's scope with filtering support"""
    query = db.query(Sale).join(Product).join(User)
    
    # Apply user scope filtering
    if current_user.role == UserRole.ADMIN:
        # Admin can see all sales
        pass
    else:
        # All users (managers and sellers) see sales from their magazine
        if not current_user.magazine_id:
            # Return empty list if user has no magazine assigned
            return []
        else:
            query = query.filter(Sale.magazine_id == current_user.magazine_id)
    
    # Apply date filtering
    if date_from:
        try:
            from_date = datetime.strptime(date_from, "%Y-%m-%d")
            query = query.filter(Sale.sale_date >= from_date)
        except ValueError:
            pass  # Ignore invalid date format
    
    if date_to:
        try:
            to_date = datetime.strptime(date_to, "%Y-%m-%d")
            # Add 1 day and subtract 1 second to include the entire end date
            to_date = to_date.replace(hour=23, minute=59, second=59)
            query = query.filter(Sale.sale_date <= to_date)
        except ValueError:
            pass  # Ignore invalid date format
    
    # Apply search filtering
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Product.name.ilike(search_term),
                Product.model.ilike(search_term),
                User.name.ilike(search_term)
            )
        )
    
    # Apply pagination and ordering
    sales = query.order_by(Sale.created_at.desc()).offset(offset).limit(limit).all()
    
    # Format response with product and seller info
    response = []
    for sale in sales:
        response.append(SaleResponse(
            id=sale.id,
            sale_price=sale.sale_price,
            sale_date=to_uzbekistan_time(sale.sale_date),
            created_at=to_uzbekistan_time(sale.created_at),
            product_id=sale.product_id,
            seller_id=sale.seller_id,
            product_name=sale.product.name,
            product_model=sale.product.model,
            seller_name=sale.seller.name,
            imei=sale.imei
        ))
    
    return response

@router.post("/", response_model=SaleResponse)
def create_sale(
    sale_data: SaleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new sale and update product inventory"""
    
    # Check if product exists and user has access
    product = db.query(Product).filter(Product.id == sale_data.product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Check permissions
    if current_user.role == UserRole.SELLER:
        # Sellers can only sell products from their manager's warehouse
        if product.manager_id != current_user.manager_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only sell products from your manager's warehouse"
            )
    elif current_user.role == UserRole.MANAGER:
        # Managers can only sell their own products
        if product.manager_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only sell your own products"
            )
    # Admin can sell any product
    
    # Check if product is in stock
    if product.count <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product is out of stock"
        )
    
    # Validate sale price
    if sale_data.sale_price <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sale price must be greater than 0"
        )
    
    try:
        # Use the current user's magazine_id
        if not current_user.magazine_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User must be assigned to a magazine to create sales"
            )
        
        # Begin transaction for atomic operation
        # Create the sale
        new_sale = Sale(
            product_id=sale_data.product_id,
            sale_price=sale_data.sale_price,
            seller_id=current_user.id,
            magazine_id=current_user.magazine_id,
            imei=sale_data.imei
        )
        
        # Update product inventory atomically
        product.count -= 1
        
        db.add(new_sale)
        db.commit()
        db.refresh(new_sale)
        
        # Create transaction record
        create_transaction(
            db=db,
            transaction_type=TransactionType.SALE,
            amount=new_sale.sale_price,
            description=f"Sale of {product.name} {product.model or ''}".strip(),
            seller_id=current_user.id,
            magazine_id=current_user.magazine_id,
            sale_id=new_sale.id,
            product_id=product.id
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create sale: {str(e)}"
        )
    
    return SaleResponse(
        id=new_sale.id,
        sale_price=new_sale.sale_price,
        sale_date=to_uzbekistan_time(new_sale.sale_date),
        created_at=to_uzbekistan_time(new_sale.created_at),
        product_id=new_sale.product_id,
        seller_id=new_sale.seller_id,
        product_name=product.name,
        product_model=product.model,
        seller_name=current_user.name,
        imei=new_sale.imei
    )

@router.get("/{sale_id}", response_model=SaleResponse)
def get_sale(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific sale by ID"""
    sale = db.query(Sale).filter(Sale.id == sale_id).first()
    
    if not sale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sale not found"
        )
    
    # Check permissions
    if current_user.role != UserRole.ADMIN:
        if sale.magazine_id != current_user.magazine_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view sales from your magazine"
            )
    # Admin can view any sale
    
    return SaleResponse(
        id=sale.id,
        sale_price=sale.sale_price,
        sale_date=to_uzbekistan_time(sale.sale_date),
        created_at=to_uzbekistan_time(sale.created_at),
        product_id=sale.product_id,
        seller_id=sale.seller_id,
        product_name=sale.product.name,
        product_model=sale.product.model,
        seller_name=sale.seller.name,
        imei=sale.imei
    ) 