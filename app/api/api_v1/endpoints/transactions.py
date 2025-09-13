from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.db.database import get_db
from app.models.transaction import Transaction, TransactionType
from app.models.auto_transaction import AutoSale, AutoLoan
from app.models.user import User, UserRole, UserType
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
    
    # Check if user is AUTO type
    is_auto_user = current_user.user_type == UserType.AUTO
    
    if is_auto_user:
        # For AUTO users, get from auto tables instead
        all_transactions = []
        
        # Get auto sales
        auto_sales = db.query(AutoSale).filter(
            AutoSale.seller_id == current_user.id
        ).order_by(AutoSale.created_at.desc()).limit(limit).all()
        
        for sale in auto_sales:
            all_transactions.append(TransactionResponse(
                id=sale.id,
                type="sale",
                amount=sale.sale_price,
                description=f"Auto sale",
                created_at=sale.created_at,
                sale_id=sale.id,
                loan_id=None,
                loan_payment_id=None,
                product_id=sale.auto_product_id,
                client_id=None,
                seller_id=sale.seller_id,
                seller_name=sale.seller.name if sale.seller else "Unknown"
            ))
            
        # Get auto loans
        auto_loans = db.query(AutoLoan).filter(
            AutoLoan.seller_id == current_user.id
        ).order_by(AutoLoan.created_at.desc()).limit(limit).all()
        
        for loan in auto_loans:
            all_transactions.append(TransactionResponse(
                id=loan.id,
                type="loan", 
                amount=loan.loan_price,
                description=f"Auto loan",
                created_at=loan.created_at,
                sale_id=None,
                loan_id=loan.id,
                loan_payment_id=None,
                product_id=loan.auto_product_id,
                client_id=loan.client_id,
                seller_id=loan.seller_id,
                seller_name=loan.seller.name if loan.seller else "Unknown"
            ))
        
        # Sort by date and limit
        all_transactions.sort(key=lambda x: x.created_at, reverse=True)
        return all_transactions[:limit]
        
    else:
        # Original logic for regular users
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
        
        # Format response for regular transactions
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
    
    # Check if user is AUTO type
    is_auto_user = current_user.user_type == UserType.AUTO
    
    if is_auto_user:
        # For AUTO users, get from auto tables instead
        all_transactions = []
        
        # Get auto sales with pagination
        offset = (page - 1) * limit
        auto_sales = db.query(AutoSale).filter(
            AutoSale.seller_id == current_user.id
        ).order_by(AutoSale.created_at.desc()).offset(offset).limit(limit).all()
        
        for sale in auto_sales:
            all_transactions.append(TransactionResponse(
                id=sale.id,
                type="sale",
                amount=sale.sale_price,
                description=f"Auto sale",
                created_at=sale.created_at,
                sale_id=sale.id,
                loan_id=None,
                loan_payment_id=None,
                product_id=sale.auto_product_id,
                client_id=None,
                seller_id=sale.seller_id,
                seller_name=sale.seller.name if sale.seller else "Unknown"
            ))
            
        # Get auto loans with pagination
        auto_loans = db.query(AutoLoan).filter(
            AutoLoan.seller_id == current_user.id
        ).order_by(AutoLoan.created_at.desc()).offset(offset).limit(limit).all()
        
        for loan in auto_loans:
            all_transactions.append(TransactionResponse(
                id=loan.id,
                type="loan", 
                amount=loan.loan_price,
                description=f"Auto loan",
                created_at=loan.created_at,
                sale_id=None,
                loan_id=loan.id,
                loan_payment_id=None,
                product_id=loan.auto_product_id,
                client_id=loan.client_id,
                seller_id=loan.seller_id,
                seller_name=loan.seller.name if loan.seller else "Unknown"
            ))
        
        # Sort by date and return
        all_transactions.sort(key=lambda x: x.created_at, reverse=True)
        return all_transactions
        
    else:
        # Original logic for regular users
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
        
        # Format response for regular transactions
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