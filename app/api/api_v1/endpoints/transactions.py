from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.db.database import get_db
from app.models.transaction import Transaction, TransactionType
from app.models.user import User, UserRole
from app.api.deps import get_current_user
from app.core.timezone import to_uzbekistan_time
from pydantic import BaseModel

router = APIRouter()

class TransactionResponse(BaseModel):
    id: int
    type: str
    amount: float
    description: str
    created_at: datetime
    sale_id: Optional[int]
    loan_id: Optional[int]
    loan_payment_id: Optional[int]
    product_id: Optional[int]
    client_id: Optional[int]
    seller_id: int
    seller_name: str
    
    class Config:
        from_attributes = True

@router.get("/recent", response_model=List[TransactionResponse])
def get_recent_transactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = 10
):
    """Get recent transactions for activity feed"""
    query = db.query(Transaction).join(User, Transaction.seller_id == User.id)
    
    if current_user.role == UserRole.ADMIN:
        # Admin can see all transactions
        transactions = query.order_by(Transaction.created_at.desc()).limit(limit).all()
    else:
        # Users see transactions from their magazine
        if not current_user.magazine_id:
            transactions = []
        else:
            transactions = query.filter(Transaction.magazine_id == current_user.magazine_id).order_by(Transaction.created_at.desc()).limit(limit).all()
    
    # Format response
    response = []
    for transaction in transactions:
        response.append(TransactionResponse(
            id=transaction.id,
            type=transaction.type.value,
            amount=transaction.amount,
            description=transaction.description,
            created_at=to_uzbekistan_time(transaction.created_at),
            sale_id=transaction.sale_id,
            loan_id=transaction.loan_id,
            loan_payment_id=transaction.loan_payment_id,
            product_id=transaction.product_id,
            client_id=transaction.client_id,
            seller_id=transaction.seller_id,
            seller_name=transaction.seller.name
        ))
    
    return response

@router.get("/", response_model=List[TransactionResponse])
def get_all_transactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    page: int = 1,
    limit: int = 50
):
    """Get all transactions with pagination"""
    query = db.query(Transaction).join(User, Transaction.seller_id == User.id)
    
    if current_user.role == UserRole.ADMIN:
        # Admin can see all transactions
        transactions = query.order_by(Transaction.created_at.desc()).offset((page - 1) * limit).limit(limit).all()
    else:
        # Users see transactions from their magazine
        if not current_user.magazine_id:
            transactions = []
        else:
            transactions = query.filter(Transaction.magazine_id == current_user.magazine_id).order_by(Transaction.created_at.desc()).offset((page - 1) * limit).limit(limit).all()
    
    # Format response
    response = []
    for transaction in transactions:
        response.append(TransactionResponse(
            id=transaction.id,
            type=transaction.type.value,
            amount=transaction.amount,
            description=transaction.description,
            created_at=to_uzbekistan_time(transaction.created_at),
            sale_id=transaction.sale_id,
            loan_id=transaction.loan_id,
            loan_payment_id=transaction.loan_payment_id,
            product_id=transaction.product_id,
            client_id=transaction.client_id,
            seller_id=transaction.seller_id,
            seller_name=transaction.seller.name
        ))
    
    return response

def create_transaction(
    db: Session,
    transaction_type: TransactionType,
    amount: float,
    description: str,
    seller_id: int,
    magazine_id: int,
    sale_id: Optional[int] = None,
    loan_id: Optional[int] = None,
    loan_payment_id: Optional[int] = None,
    product_id: Optional[int] = None,
    client_id: Optional[int] = None
):
    """Helper function to create transaction records"""
    transaction = Transaction(
        type=transaction_type,
        amount=amount,
        description=description,
        seller_id=seller_id,
        magazine_id=magazine_id,
        sale_id=sale_id,
        loan_id=loan_id,
        loan_payment_id=loan_payment_id,
        product_id=product_id,
        client_id=client_id
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction