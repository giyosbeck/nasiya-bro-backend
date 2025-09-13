from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import json
from app.db.database import get_db
from app.models.user import User, UserType
from app.models.auto_product import AutoProduct
from app.models.auto_transaction import AutoLoan, AutoLoanPayment
from app.models.user import Client
from app.api.deps import get_current_user
from pydantic import BaseModel
from app.models.transaction import PaymentStatus
from datetime import datetime

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

class AutoLoanCalculate(BaseModel):
    loan_price: float
    initial_payment: float
    loan_months: int
    yearly_interest_rate: float

class AutoLoanCalculationResponse(BaseModel):
    loan_amount: float  # remaining amount after initial payment
    monthly_payment: float
    total_amount: float  # total amount to be paid
    total_interest: float  # total interest amount

class QuickPaymentRequest(BaseModel):
    amount: float
    payment_date: str = None

class PaymentResponse(BaseModel):
    id: int
    amount: float
    payment_date: datetime = None
    due_date: datetime
    status: str
    is_late: bool
    is_full_payment: bool
    loan_id: int

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
    agreement_images: Optional[List[str]] = None
    is_completed: bool
    seller_id: int
    car_name: str
    model: str
    color: str
    year: int
    seller_name: str
    client_name: str
    
    class Config:
        from_attributes = True

@router.post("/calculate", response_model=AutoLoanCalculationResponse)
def calculate_auto_loan(
    calculation_data: AutoLoanCalculate,
    current_user: User = Depends(get_current_user)
):
    """Calculate auto loan payments with yearly interest rate"""
    # Only allow auto users to calculate auto loans
    if current_user.user_type != UserType.AUTO:
        raise HTTPException(
            status_code=403,
            detail="Only auto users can calculate auto loans"
        )
    
    # Calculate remaining amount after initial payment
    remaining_amount = calculation_data.loan_price - calculation_data.initial_payment
    
    if remaining_amount <= 0:
        raise HTTPException(
            status_code=400,
            detail="Initial payment cannot be greater than or equal to loan price"
        )
    
    # Calculate using simple interest: Total = Principal + (Principal × Rate × Time)
    yearly_interest_rate = calculation_data.yearly_interest_rate / 100
    
    if yearly_interest_rate > 0:
        # Simple interest calculation for 1 year
        total_interest = remaining_amount * yearly_interest_rate
        total_amount = remaining_amount + total_interest
        monthly_payment = total_amount / calculation_data.loan_months
    else:
        # No interest case
        total_interest = 0
        total_amount = remaining_amount
        monthly_payment = remaining_amount / calculation_data.loan_months
    
    return AutoLoanCalculationResponse(
        loan_amount=remaining_amount,
        monthly_payment=round(monthly_payment, 2),
        total_amount=round(total_amount, 2),
        total_interest=round(total_interest, 2)
    )

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
    print(f"DEBUG auto_loan: Querying product_id={loan_data.auto_product_id}, user_id={current_user.id}")
    
    # Direct database query to check actual values
    from sqlalchemy import text
    result = db.execute(text("SELECT id, car_name, count FROM auto_products WHERE id = :id"), {"id": loan_data.auto_product_id})
    direct_result = result.fetchone()
    print(f"DEBUG auto_loan: Direct DB query result: {direct_result}")
    
    # Force fresh query to avoid stale session data
    db.expire_all()
    auto_product = db.query(AutoProduct).filter(
        AutoProduct.id == loan_data.auto_product_id,
        AutoProduct.manager_id == current_user.id
    ).first()
    
    if not auto_product:
        print(f"DEBUG auto_loan: Product not found - product_id={loan_data.auto_product_id}")
        raise HTTPException(
            status_code=404,
            detail="Auto product not found"
        )
    
    # Check if there's enough stock
    print(f"DEBUG auto_loan: Found product - id={auto_product.id}, car_name={auto_product.car_name}, count={auto_product.count}")
    if auto_product.count <= 0:
        raise HTTPException(
            status_code=400,
            detail=f"No stock available for this car. Current count: {auto_product.count}"
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
    
    # Calculate using simple interest: Total = Principal + (Principal × Rate × Time)
    yearly_interest_rate = loan_data.yearly_interest_rate / 100
    if yearly_interest_rate > 0:
        # Simple interest calculation for 1 year
        total_interest = remaining_amount * yearly_interest_rate
        total_amount = remaining_amount + total_interest
        monthly_payment = total_amount / loan_data.loan_months
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
        seller_id=current_user.id
    )
    
    db.add(new_loan)
    db.flush()  # Get the loan ID
    
    # Create payment schedule
    for month in range(1, loan_data.loan_months + 1):
        due_date = new_loan.loan_start_date + relativedelta(months=month)
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
    
    # Return proper response with all required fields
    agreement_images = None
    if new_loan.agreement_images:
        try:
            agreement_images = json.loads(new_loan.agreement_images)
        except json.JSONDecodeError:
            agreement_images = []
    
    return AutoLoanResponse(
        id=new_loan.id,
        auto_product_id=new_loan.auto_product_id,
        client_id=new_loan.client_id,
        loan_price=new_loan.loan_price,
        initial_payment=new_loan.initial_payment,
        remaining_amount=new_loan.remaining_amount,
        loan_months=new_loan.loan_months,
        yearly_interest_rate=new_loan.yearly_interest_rate,
        monthly_payment=new_loan.monthly_payment,
        loan_start_date=new_loan.loan_start_date,
        video_url=new_loan.video_url,
        agreement_images=agreement_images,
        is_completed=new_loan.is_completed,
        seller_id=new_loan.seller_id,
        car_name=auto_product.car_name,
        model=auto_product.model,
        color=auto_product.color,
        year=auto_product.year,
        seller_name=current_user.name,
        client_name=client.name
    )

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
    
    results = db.query(
        AutoLoan,
        AutoProduct.car_name,
        AutoProduct.model,
        AutoProduct.color,
        AutoProduct.year,
        User.name.label('seller_name'),
        Client.name.label('client_name')
    ).join(AutoProduct, AutoLoan.auto_product_id == AutoProduct.id
    ).join(User, AutoLoan.seller_id == User.id
    ).join(Client, AutoLoan.client_id == Client.id
    ).filter(
        AutoLoan.seller_id == current_user.id
    ).all()
    
    response = []
    for loan, car_name, model, color, year, seller_name, client_name in results:
        # Safely parse JSON agreement_images
        agreement_images = None
        if loan.agreement_images:
            try:
                agreement_images = json.loads(loan.agreement_images)
            except json.JSONDecodeError:
                agreement_images = []
        
        response.append(AutoLoanResponse(
            id=loan.id,
            auto_product_id=loan.auto_product_id,
            client_id=loan.client_id,
            loan_price=loan.loan_price,
            initial_payment=loan.initial_payment,
            remaining_amount=loan.remaining_amount,
            loan_months=loan.loan_months,
            yearly_interest_rate=loan.yearly_interest_rate,
            monthly_payment=loan.monthly_payment,
            loan_start_date=loan.loan_start_date,
            video_url=loan.video_url,
            agreement_images=agreement_images,
            is_completed=loan.is_completed,
            seller_id=loan.seller_id,
            car_name=car_name,
            model=model,
            color=color,
            year=year,
            seller_name=seller_name,
            client_name=client_name
        ))
    
    return response

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
    
    result = db.query(
        AutoLoan,
        AutoProduct.car_name,
        AutoProduct.model,
        AutoProduct.color,
        AutoProduct.year,
        User.name.label('seller_name'),
        Client.name.label('client_name')
    ).join(AutoProduct, AutoLoan.auto_product_id == AutoProduct.id
    ).join(User, AutoLoan.seller_id == User.id
    ).join(Client, AutoLoan.client_id == Client.id
    ).filter(
        AutoLoan.id == loan_id,
        AutoLoan.seller_id == current_user.id
    ).first()
    
    if not result:
        raise HTTPException(
            status_code=404,
            detail="Auto loan not found"
        )
    
    loan, car_name, model, color, year, seller_name, client_name = result
    
    # Safely parse JSON agreement_images
    agreement_images = None
    if loan.agreement_images:
        try:
            agreement_images = json.loads(loan.agreement_images)
        except json.JSONDecodeError:
            # Handle malformed JSON gracefully
            agreement_images = []
    
    return AutoLoanResponse(
        id=loan.id,
        auto_product_id=loan.auto_product_id,
        client_id=loan.client_id,
        loan_price=loan.loan_price,
        initial_payment=loan.initial_payment,
        remaining_amount=loan.remaining_amount,
        loan_months=loan.loan_months,
        yearly_interest_rate=loan.yearly_interest_rate,
        monthly_payment=loan.monthly_payment,
        loan_start_date=loan.loan_start_date,
        video_url=loan.video_url,
        agreement_images=agreement_images,
        is_completed=loan.is_completed,
        seller_id=loan.seller_id,
        car_name=car_name,
        model=model,
        color=color,
        year=year,
        seller_name=seller_name,
        client_name=client_name
    )

@router.get("/{loan_id}/payments", response_model=List[dict])
def get_auto_loan_payments(
    loan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all payments for a specific auto loan"""
    if current_user.user_type != UserType.AUTO:
        raise HTTPException(
            status_code=403,
            detail="Only auto users can access auto loan payments"
        )
    
    # Check if auto loan exists and user has access
    auto_loan = db.query(AutoLoan).filter(
        AutoLoan.id == loan_id,
        AutoLoan.seller_id == current_user.id
    ).first()
    
    if not auto_loan:
        raise HTTPException(
            status_code=404,
            detail="Auto loan not found"
        )
    
    payments = db.query(AutoLoanPayment).filter(
        AutoLoanPayment.auto_loan_id == loan_id
    ).order_by(AutoLoanPayment.due_date).all()
    
    return [
        {
            "id": payment.id,
            "amount": payment.amount,
            "payment_date": payment.payment_date,
            "due_date": payment.due_date,
            "status": payment.status.value,
            "is_late": payment.is_late,
            "is_full_payment": payment.is_full_payment,
            "loan_id": loan_id  # Return the auto loan ID
        }
        for payment in payments
    ]

@router.post("/{loan_id}/payments/{payment_id}/mark-paid", response_model=PaymentResponse)
def mark_auto_payment_paid(
    loan_id: int,
    payment_id: int,
    payment_request: QuickPaymentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark an auto loan payment as paid with specified amount"""
    # Only allow auto users to mark auto loan payments
    if current_user.user_type != UserType.AUTO:
        raise HTTPException(
            status_code=403,
            detail="Only auto users can mark auto loan payments"
        )
    
    # Check if auto loan exists and user has access
    auto_loan = db.query(AutoLoan).filter(
        AutoLoan.id == loan_id,
        AutoLoan.seller_id == current_user.id
    ).first()
    if not auto_loan:
        raise HTTPException(status_code=404, detail="Auto loan not found")
    
    # Get the payment record
    payment = db.query(AutoLoanPayment).filter(
        AutoLoanPayment.id == payment_id,
        AutoLoanPayment.auto_loan_id == loan_id
    ).first()
    
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    if payment.status == PaymentStatus.PAID:
        raise HTTPException(status_code=400, detail="Payment already recorded")
    
    # Validate payment amount
    if payment_request.amount <= 0:
        raise HTTPException(status_code=400, detail="Payment amount must be greater than 0")
    
    try:
        # Parse payment date or use current date
        if payment_request.payment_date:
            payment_datetime = datetime.fromisoformat(payment_request.payment_date.replace('Z', '+00:00'))
        else:
            payment_datetime = datetime.now()
        
        # Update payment record
        payment.payment_date = payment_datetime
        payment.amount = payment_request.amount
        payment.status = PaymentStatus.PAID
        
        # Update auto loan remaining balance
        auto_loan.remaining_amount -= payment_request.amount
        
        # Check if loan is completed
        if auto_loan.remaining_amount <= 0:
            auto_loan.is_completed = True
            auto_loan.remaining_amount = 0
        
        db.commit()
        db.refresh(payment)
        
        return PaymentResponse(
            id=payment.id,
            amount=payment.amount,
            payment_date=payment.payment_date,
            due_date=payment.due_date,
            status=payment.status.value,
            is_late=payment.is_late,
            is_full_payment=payment.is_full_payment,
            loan_id=loan_id
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to mark payment as paid: {str(e)}")

@router.post("/{loan_id}/pay-full", response_model=dict)
def pay_full_auto_loan(
    loan_id: int,
    payment_request: QuickPaymentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Pay the full remaining balance of an auto loan"""
    # Only allow auto users to pay full auto loans
    if current_user.user_type != UserType.AUTO:
        raise HTTPException(
            status_code=403,
            detail="Only auto users can pay full auto loans"
        )
    
    # Check if auto loan exists and user has access
    auto_loan = db.query(AutoLoan).filter(
        AutoLoan.id == loan_id,
        AutoLoan.seller_id == current_user.id
    ).first()
    if not auto_loan:
        raise HTTPException(status_code=404, detail="Auto loan not found")
    
    if auto_loan.is_completed:
        raise HTTPException(status_code=400, detail="Auto loan is already completed")
    
    # Validate payment amount
    if payment_request.amount <= 0:
        raise HTTPException(status_code=400, detail="Payment amount must be greater than 0")
    
    try:
        # Parse payment date or use current date
        if payment_request.payment_date:
            payment_datetime = datetime.fromisoformat(payment_request.payment_date.replace('Z', '+00:00'))
        else:
            payment_datetime = datetime.now()
        
        # Mark all pending payments as paid
        pending_payments = db.query(AutoLoanPayment).filter(
            AutoLoanPayment.auto_loan_id == loan_id,
            AutoLoanPayment.status == PaymentStatus.PENDING
        ).all()
        
        for payment in pending_payments:
            payment.payment_date = payment_datetime
            payment.status = PaymentStatus.PAID
            payment.is_full_payment = True
        
        # Update auto loan
        auto_loan.remaining_amount = 0
        auto_loan.is_completed = True
        
        db.commit()
        
        return {
            "message": "Auto loan paid in full successfully",
            "loan_id": loan_id,
            "amount_paid": payment_request.amount,
            "payment_date": payment_datetime.isoformat()
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to pay full loan: {str(e)}")