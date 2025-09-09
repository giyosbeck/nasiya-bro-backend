from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
from app.db.database import get_db
from app.models.user import User, UserType
from app.models.auto_product import AutoProduct
from app.models.auto_transaction import AutoLoan, AutoLoanPayment
from app.models.user import Client
from app.api.deps import get_current_user
from pydantic import BaseModel
from app.models.transaction import PaymentStatus

router = APIRouter()

class AutoLoanCreate(BaseModel):
    auto_product_id: int
    client_id: int
    loan_price: float
    initial_payment: float
    loan_months: int
    yearly_interest_rate: float  # Gadavoy foiz
    video_url: str = None
    agreement_images: str = None  # JSON string

class AutoLoanResponse(BaseModel):
    id: int
    auto_product_id: int
    client_id: int
    loan_price: float
    initial_payment: float
    remaining_amount: float
    loan_months: int
    yearly_interest_rate: float
    monthly_payment: float
    loan_start_date: datetime
    video_url: str = None
    agreement_images: str = None
    is_completed: bool
    seller_id: int
    magazine_id: int
    
    class Config:
        from_attributes = True

@router.post("/", response_model=AutoLoanResponse)
def create_auto_loan(
    loan_data: AutoLoanCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new auto loan"""
    # Only allow auto users to create auto loans
    if current_user.user_type != UserType.AUTO:
        raise HTTPException(
            status_code=403,
            detail="Only auto users can create auto loans"
        )
    
    # Verify auto product exists and belongs to user
    auto_product = db.query(AutoProduct).filter(
        AutoProduct.id == loan_data.auto_product_id,
        AutoProduct.manager_id == current_user.id
    ).first()
    
    if not auto_product:
        raise HTTPException(
            status_code=404,
            detail="Auto product not found"
        )
    
    # Check if there's enough stock
    if auto_product.count <= 0:
        raise HTTPException(
            status_code=400,
            detail="No stock available for this car"
        )
    
    # Verify client exists
    client = db.query(Client).filter(Client.id == loan_data.client_id).first()
    if not client:
        raise HTTPException(
            status_code=404,
            detail="Client not found"
        )
    
    # Calculate remaining amount and monthly payment
    remaining_amount = loan_data.loan_price - loan_data.initial_payment
    
    # Calculate monthly payment with yearly interest rate
    monthly_interest_rate = loan_data.yearly_interest_rate / 100 / 12
    if monthly_interest_rate > 0:
        # Standard loan payment formula
        monthly_payment = remaining_amount * (
            monthly_interest_rate * (1 + monthly_interest_rate)**loan_data.loan_months
        ) / ((1 + monthly_interest_rate)**loan_data.loan_months - 1)
    else:
        # Interest-free loan
        monthly_payment = remaining_amount / loan_data.loan_months
    
    # Create auto loan
    new_loan = AutoLoan(
        auto_product_id=loan_data.auto_product_id,
        client_id=loan_data.client_id,
        loan_price=loan_data.loan_price,
        initial_payment=loan_data.initial_payment,
        remaining_amount=remaining_amount,
        loan_months=loan_data.loan_months,
        yearly_interest_rate=loan_data.yearly_interest_rate,
        monthly_payment=monthly_payment,
        loan_start_date=datetime.now(),
        video_url=loan_data.video_url,
        agreement_images=loan_data.agreement_images,
        seller_id=current_user.id,
        magazine_id=current_user.magazine_id
    )
    
    db.add(new_loan)
    db.flush()  # Get the loan ID
    
    # Create payment schedule
    for month in range(1, loan_data.loan_months + 1):
        due_date = new_loan.loan_start_date + timedelta(days=30 * month)
        payment = AutoLoanPayment(
            auto_loan_id=new_loan.id,
            amount=monthly_payment,
            due_date=due_date,
            status=PaymentStatus.PENDING
        )
        db.add(payment)
    
    # Reduce auto product stock
    auto_product.count -= 1
    
    db.commit()
    db.refresh(new_loan)
    
    return new_loan

@router.get("/", response_model=List[AutoLoanResponse])
def get_auto_loans(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all auto loans for the current user"""
    if current_user.user_type != UserType.AUTO:
        raise HTTPException(
            status_code=403,
            detail="Only auto users can access auto loans"
        )
    
    loans = db.query(AutoLoan).filter(
        AutoLoan.seller_id == current_user.id
    ).all()
    
    return loans

@router.get("/{loan_id}", response_model=AutoLoanResponse)
def get_auto_loan(
    loan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific auto loan"""
    if current_user.user_type != UserType.AUTO:
        raise HTTPException(
            status_code=403,
            detail="Only auto users can access auto loans"
        )
    
    loan = db.query(AutoLoan).filter(
        AutoLoan.id == loan_id,
        AutoLoan.seller_id == current_user.id
    ).first()
    
    if not loan:
        raise HTTPException(
            status_code=404,
            detail="Auto loan not found"
        )
    
    return loan