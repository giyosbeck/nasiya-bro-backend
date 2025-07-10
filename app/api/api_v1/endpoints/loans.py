from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import json
from app.db.database import get_db
from app.models.transaction import Loan, LoanPayment, TransactionType, PaymentStatus
from app.models.product import Product
from app.models.user import User, UserRole, Client
from app.api.deps import get_current_user
from app.api.api_v1.endpoints.transactions import create_transaction
from app.core.timezone import to_uzbekistan_time
from pydantic import BaseModel

router = APIRouter()

class LoanCreate(BaseModel):
    product_id: int
    client_id: int
    loan_price: float
    initial_payment: float
    loan_months: int
    loan_start_date: datetime
    video_url: Optional[str] = None
    agreement_images: Optional[List[str]] = None

class LoanResponse(BaseModel):
    id: int
    loan_price: float
    initial_payment: float
    remaining_amount: float
    loan_months: int
    monthly_payment: float
    loan_start_date: datetime
    created_at: datetime
    is_completed: bool
    product_id: int
    client_id: int
    seller_id: int
    product_name: str
    product_model: str
    client_name: str
    client_phone: str
    seller_name: str
    video_url: Optional[str]
    agreement_images: Optional[List[str]]
    
    class Config:
        from_attributes = True

class LoanCalculation(BaseModel):
    loan_amount: float
    monthly_payment: float
    total_amount: float

class PaymentCreate(BaseModel):
    amount: float
    payment_date: datetime

class QuickPaymentRequest(BaseModel):
    amount: float
    payment_date: Optional[str] = None

class PaymentResponse(BaseModel):
    id: int
    amount: float
    payment_date: Optional[datetime]
    due_date: datetime
    status: str
    is_late: bool
    is_full_payment: bool
    loan_id: int
    
    class Config:
        from_attributes = True

def calculate_loan_payment(principal: float, months: int) -> float:
    """Calculate monthly payment using simple division (no interest)"""
    if months <= 0:
        raise ValueError("Loan months must be greater than 0")
    if principal < 0:
        raise ValueError("Principal amount must be non-negative")
    
    # Calculate monthly payment with proper rounding
    monthly_payment = principal / months
    return round(monthly_payment, 2)

def generate_payment_schedule(db: Session, loan: Loan) -> None:
    """Generate payment schedule for a loan"""
    from datetime import timedelta
    
    # Calculate due dates for each month (approximate 30 days per month)
    base_due_date = loan.loan_start_date.date() + timedelta(days=30)
    
    for month in range(loan.loan_months):
        # Calculate due date for this payment (month * 30 days)
        due_date = base_due_date + timedelta(days=month * 30)
        
        # Create payment record with status as "pending"
        payment = LoanPayment(
            loan_id=loan.id,
            amount=loan.monthly_payment,
            due_date=datetime.combine(due_date, datetime.min.time()),
            payment_date=None,  # Will be set when payment is made
            status=PaymentStatus.PENDING,
            is_late=False
        )
        
        db.add(payment)
    
    db.commit()

@router.post("/calculate", response_model=LoanCalculation)
def calculate_loan(
    loan_price: float,
    initial_payment: float,
    loan_months: int
):
    """Calculate loan payment details"""
    # Input validation
    if loan_price <= 0:
        raise HTTPException(status_code=400, detail="Loan price must be greater than 0")
    if initial_payment < 0:
        raise HTTPException(status_code=400, detail="Initial payment cannot be negative")
    if initial_payment >= loan_price:
        raise HTTPException(status_code=400, detail="Initial payment must be less than loan price")
    if loan_months <= 0 or loan_months > 240:  # Max 20 years
        raise HTTPException(status_code=400, detail="Loan months must be between 1 and 240")
    
    remaining_amount = loan_price - initial_payment
    monthly_payment = calculate_loan_payment(remaining_amount, loan_months)
    
    # Ensure total calculation is accurate
    total_amount = initial_payment + (monthly_payment * loan_months)
    
    return LoanCalculation(
        loan_amount=remaining_amount,
        monthly_payment=monthly_payment,
        total_amount=total_amount
    )

@router.get("/", response_model=List[LoanResponse])
def get_loans(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    page: int = 1,
    limit: int = 10
):
    """Get all loans for the current user's scope"""
    query = db.query(Loan).join(Product).join(Client).join(User)
    
    if current_user.role == UserRole.ADMIN:
        # Admin can see all loans
        loans = query.order_by(Loan.created_at.desc()).offset((page - 1) * limit).limit(limit).all()
    else:
        # All users (managers and sellers) see loans from their magazine
        if not current_user.magazine_id:
            # Return empty list if user has no magazine assigned
            loans = []
        else:
            loans = query.filter(Loan.magazine_id == current_user.magazine_id).order_by(Loan.created_at.desc()).offset((page - 1) * limit).limit(limit).all()
    
    # Format response with related info
    response = []
    for loan in loans:
        # Safely parse JSON agreement_images
        agreement_images = None
        if loan.agreement_images:
            try:
                agreement_images = json.loads(loan.agreement_images)
            except json.JSONDecodeError:
                # Handle malformed JSON gracefully
                agreement_images = []
        
        response.append(LoanResponse(
            id=loan.id,
            loan_price=loan.loan_price,
            initial_payment=loan.initial_payment,
            remaining_amount=loan.remaining_amount,
            loan_months=loan.loan_months,
            monthly_payment=loan.monthly_payment,
            loan_start_date=to_uzbekistan_time(loan.loan_start_date),
            created_at=to_uzbekistan_time(loan.created_at),
            is_completed=loan.is_completed,
            product_id=loan.product_id,
            client_id=loan.client_id,
            seller_id=loan.seller_id,
            product_name=loan.product.name,
            product_model=loan.product.model,
            client_name=loan.client.name,
            client_phone=loan.client.phone,
            seller_name=loan.seller.name,
            video_url=loan.video_url,
            agreement_images=agreement_images
        ))
    
    return response

@router.post("/", response_model=LoanResponse)
def create_loan(
    loan_data: LoanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new loan and update product inventory"""
    
    # Check if product exists and user has access
    product = db.query(Product).filter(Product.id == loan_data.product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Check if client exists
    client = db.query(Client).filter(Client.id == loan_data.client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    # Check permissions
    if current_user.role == UserRole.SELLER:
        # Sellers can only create loans for products from their manager's warehouse
        if product.manager_id != current_user.manager_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only create loans for products from your manager's warehouse"
            )
    elif current_user.role == UserRole.MANAGER:
        # Managers can only create loans for their own products
        if product.manager_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only create loans for your own products"
            )
    # Admin can create loans for any product
    
    # Check if product is in stock
    if product.count <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product is out of stock"
        )
    
    # Enhanced loan data validation
    if loan_data.loan_price <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Loan price must be greater than 0"
        )
    if loan_data.initial_payment < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Initial payment cannot be negative"
        )
    if loan_data.initial_payment >= loan_data.loan_price:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Initial payment cannot be greater than or equal to loan price"
        )
    if loan_data.loan_months <= 0 or loan_data.loan_months > 240:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Loan months must be between 1 and 240"
        )
    
    # Calculate loan details
    remaining_amount = loan_data.loan_price - loan_data.initial_payment
    monthly_payment = calculate_loan_payment(remaining_amount, loan_data.loan_months)
    
    try:
        # Use the current user's magazine_id
        if not current_user.magazine_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User must be assigned to a magazine to create loans"
            )
        
        # Begin transaction for atomic operation
        # Create the loan
        new_loan = Loan(
            product_id=loan_data.product_id,
            client_id=loan_data.client_id,
            seller_id=current_user.id,
            magazine_id=current_user.magazine_id,
            loan_price=loan_data.loan_price,
            initial_payment=loan_data.initial_payment,
            remaining_amount=remaining_amount,
            loan_months=loan_data.loan_months,
            monthly_payment=monthly_payment,
            loan_start_date=loan_data.loan_start_date,
            video_url=loan_data.video_url,
            agreement_images=json.dumps(loan_data.agreement_images) if loan_data.agreement_images else None
        )
        
        # Update product inventory atomically
        product.count -= 1
        
        db.add(new_loan)
        db.commit()
        db.refresh(new_loan)
        
        # Generate payment schedule for the loan
        generate_payment_schedule(db, new_loan)
        
        # Create transaction record for loan creation
        create_transaction(
            db=db,
            transaction_type=TransactionType.LOAN,
            amount=new_loan.loan_price,
            description=f"Loan created for {client.name} - {product.name} {product.model or ''}".strip(),
            seller_id=current_user.id,
            magazine_id=current_user.magazine_id,
            loan_id=new_loan.id,
            product_id=product.id,
            client_id=client.id
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create loan: {str(e)}"
        )
    
    return LoanResponse(
        id=new_loan.id,
        loan_price=new_loan.loan_price,
        initial_payment=new_loan.initial_payment,
        remaining_amount=new_loan.remaining_amount,
        loan_months=new_loan.loan_months,
        monthly_payment=new_loan.monthly_payment,
        loan_start_date=to_uzbekistan_time(new_loan.loan_start_date),
        created_at=to_uzbekistan_time(new_loan.created_at),
        is_completed=new_loan.is_completed,
        product_id=new_loan.product_id,
        client_id=new_loan.client_id,
        seller_id=new_loan.seller_id,
        product_name=product.name,
        product_model=product.model,
        client_name=client.name,
        seller_name=current_user.name,
        video_url=new_loan.video_url,
        agreement_images=json.loads(new_loan.agreement_images) if new_loan.agreement_images else None
    )

@router.get("/{loan_id}", response_model=LoanResponse)
def get_loan(
    loan_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific loan by ID"""
    loan = db.query(Loan).filter(Loan.id == loan_id).first()
    
    if not loan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Loan not found"
        )
    
    # Check permissions
    if current_user.role != UserRole.ADMIN:
        if loan.magazine_id != current_user.magazine_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view loans from your magazine"
            )
    # Admin can view any loan
    
    agreement_images = json.loads(loan.agreement_images) if loan.agreement_images else None
    
    # Convert relative paths to full URLs
    base_url = f"{request.url.scheme}://{request.url.netloc}/api/v1/files/serve"
    video_url = f"{base_url}/{loan.video_url}" if loan.video_url else None
    full_agreement_images = [f"{base_url}/{img}" for img in agreement_images] if agreement_images else None
    
    return LoanResponse(
        id=loan.id,
        loan_price=loan.loan_price,
        initial_payment=loan.initial_payment,
        remaining_amount=loan.remaining_amount,
        loan_months=loan.loan_months,
        monthly_payment=loan.monthly_payment,
        loan_start_date=to_uzbekistan_time(loan.loan_start_date),
        created_at=to_uzbekistan_time(loan.created_at),
        is_completed=loan.is_completed,
        product_id=loan.product_id,
        client_id=loan.client_id,
        seller_id=loan.seller_id,
        product_name=loan.product.name,
        product_model=loan.product.model,
        client_name=loan.client.name,
        client_phone=loan.client.phone,
        seller_name=loan.seller.name,
        video_url=video_url,
        agreement_images=full_agreement_images
    )

# Payment Management Endpoints

@router.get("/{loan_id}/payments", response_model=List[PaymentResponse])
def get_loan_payments(
    loan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all payments for a specific loan"""
    # Check if loan exists and user has access
    loan = db.query(Loan).filter(Loan.id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    
    # Check permissions
    if current_user.role != UserRole.ADMIN:
        if loan.magazine_id != current_user.magazine_id:
            raise HTTPException(status_code=403, detail="Access denied")
    
    payments = db.query(LoanPayment).filter(LoanPayment.loan_id == loan_id).order_by(LoanPayment.due_date).all()
    
    return [
        PaymentResponse(
            id=payment.id,
            amount=payment.amount,
            payment_date=payment.payment_date,
            due_date=payment.due_date,
            status=payment.status.value,
            is_late=payment.is_late,
            is_full_payment=payment.is_full_payment,
            loan_id=payment.loan_id
        )
        for payment in payments
    ]

@router.post("/{loan_id}/payments/{payment_id}/record", response_model=PaymentResponse)
def record_payment(
    loan_id: int,
    payment_id: int,
    payment_data: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Record a payment for a loan"""
    # Check if loan exists and user has access
    loan = db.query(Loan).filter(Loan.id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    
    # Check permissions
    if current_user.role != UserRole.ADMIN:
        if loan.magazine_id != current_user.magazine_id:
            raise HTTPException(status_code=403, detail="Access denied")
    
    # Get the payment record
    payment = db.query(LoanPayment).filter(
        LoanPayment.id == payment_id,
        LoanPayment.loan_id == loan_id
    ).first()
    
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    if payment.status == PaymentStatus.PAID:
        raise HTTPException(status_code=400, detail="Payment already recorded")
    
    # Validate payment amount
    if payment_data.amount <= 0:
        raise HTTPException(status_code=400, detail="Payment amount must be greater than 0")
    
    try:
        # Update payment record
        payment.payment_date = payment_data.payment_date
        payment.amount = payment_data.amount  # Allow partial payments
        payment.status = PaymentStatus.PAID
        
        # Update loan remaining balance
        loan.remaining_amount -= payment_data.amount
        
        # Check if loan is completed
        if loan.remaining_amount <= 0:
            loan.is_completed = True
            loan.remaining_amount = 0  # Ensure it doesn't go negative
        
        db.commit()
        
        # Create transaction record for payment
        create_transaction(
            db=db,
            transaction_type=TransactionType.LOAN_PAYMENT,
            amount=payment_data.amount,
            description=f"Payment received for loan #{loan.id} - {loan.client.name}",
            seller_id=current_user.id,
            magazine_id=current_user.magazine_id,
            loan_id=loan.id,
            loan_payment_id=payment.id,
            client_id=loan.client_id
        )
        
        db.refresh(payment)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to record payment: {str(e)}")
    
    return PaymentResponse(
        id=payment.id,
        amount=payment.amount,
        payment_date=payment.payment_date,
        due_date=payment.due_date,
        status=payment.status.value,
        is_late=payment.is_late,
        is_full_payment=payment.is_full_payment,
        loan_id=payment.loan_id
    )

@router.get("/payments/overdue", response_model=List[dict])
def get_overdue_payments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all overdue payments for the user's magazine"""
    from datetime import date
    
    # Build base query
    query = db.query(LoanPayment).join(Loan).filter(
        LoanPayment.status == PaymentStatus.PENDING,
        LoanPayment.due_date < datetime.now(),
        Loan.is_completed == False
    )
    
    # Filter by magazine for non-admin users
    if current_user.role != UserRole.ADMIN:
        query = query.filter(Loan.magazine_id == current_user.magazine_id)
    
    overdue_payments = query.all()
    
    # Update overdue status
    for payment in overdue_payments:
        if not payment.is_late:
            payment.is_late = True
            payment.status = PaymentStatus.OVERDUE
    
    db.commit()
    
    # Return detailed information
    result = []
    for payment in overdue_payments:
        result.append({
            "payment_id": payment.id,
            "loan_id": payment.loan_id,
            "client_name": payment.loan.client.name,
            "client_phone": payment.loan.client.phone,
            "product_name": payment.loan.product.name,
            "amount": payment.amount,
            "due_date": payment.due_date.isoformat(),
            "days_overdue": (datetime.now().date() - payment.due_date.date()).days,
            "remaining_balance": payment.loan.remaining_amount
        })
    
    return result

@router.get("/payments/upcoming", response_model=List[dict])
def get_upcoming_payments(
    days: int = 7,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get payments due in the next X days"""
    from datetime import date, timedelta
    
    end_date = datetime.now() + timedelta(days=days)
    
    # Build base query
    query = db.query(LoanPayment).join(Loan).filter(
        LoanPayment.status == PaymentStatus.PENDING,
        LoanPayment.due_date <= end_date,
        LoanPayment.due_date >= datetime.now(),
        Loan.is_completed == False
    )
    
    # Filter by magazine for non-admin users
    if current_user.role != UserRole.ADMIN:
        query = query.filter(Loan.magazine_id == current_user.magazine_id)
    
    upcoming_payments = query.order_by(LoanPayment.due_date).all()
    
    # Return detailed information
    result = []
    for payment in upcoming_payments:
        result.append({
            "payment_id": payment.id,
            "loan_id": payment.loan_id,
            "client_name": payment.loan.client.name,
            "client_phone": payment.loan.client.phone,
            "product_name": payment.loan.product.name,
            "amount": payment.amount,
            "due_date": payment.due_date.isoformat(),
            "days_until_due": (payment.due_date.date() - datetime.now().date()).days,
            "remaining_balance": payment.loan.remaining_amount
        })
    
    return result

@router.get("/active-payments", response_model=List[dict])
def get_active_loans_with_payments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all loans with pending payments (for homepage display)"""
    from datetime import date
    
    # Build base query for loans with pending payments
    query = db.query(LoanPayment).join(Loan).filter(
        LoanPayment.status.in_([PaymentStatus.PENDING, PaymentStatus.OVERDUE]),
        Loan.is_completed == False
    )
    
    # Filter by magazine for non-admin users
    if current_user.role != UserRole.ADMIN:
        query = query.filter(Loan.magazine_id == current_user.magazine_id)
    
    # Get next payment for each loan (order by due date)
    payments = query.order_by(LoanPayment.due_date).all()
    
    # Group by loan and get first (next) payment for each loan
    loans_data = {}
    today = date.today()
    
    for payment in payments:
        if payment.loan_id not in loans_data:
            payment_date = payment.due_date.date() if hasattr(payment.due_date, 'date') else payment.due_date
            days_until_due = (payment_date - today).days
            is_overdue = days_until_due < 0
            
            loans_data[payment.loan_id] = {
                "loan_id": payment.loan_id,
                "client_name": payment.loan.client.name,
                "client_phone": payment.loan.client.phone,
                "product_name": payment.loan.product.name,
                "next_payment_amount": payment.amount,
                "next_payment_date": payment.due_date.isoformat(),
                "days_until_due": abs(days_until_due) if is_overdue else days_until_due,
                "is_overdue": is_overdue,
                "total_remaining": payment.loan.remaining_amount
            }
    
    # Convert to list and sort by urgency (overdue first, then by due date)
    result = list(loans_data.values())
    result.sort(key=lambda x: (not x["is_overdue"], x["days_until_due"]))
    
    return result

@router.post("/{loan_id}/payments/{payment_id}/mark-paid", response_model=PaymentResponse)
def mark_payment_paid(
    loan_id: int,
    payment_id: int,
    payment_request: QuickPaymentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark a payment as paid with specified amount"""
    # Check if loan exists and user has access
    loan = db.query(Loan).filter(Loan.id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    
    # Check permissions
    if current_user.role != UserRole.ADMIN:
        if loan.magazine_id != current_user.magazine_id:
            raise HTTPException(status_code=403, detail="Access denied")
    
    # Get the payment record
    payment = db.query(LoanPayment).filter(
        LoanPayment.id == payment_id,
        LoanPayment.loan_id == loan_id
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
        
        # Update loan remaining balance
        loan.remaining_amount -= payment_request.amount
        
        # Check if loan is completed
        if loan.remaining_amount <= 0:
            loan.is_completed = True
            loan.remaining_amount = 0
        
        db.commit()
        
        # Create transaction record for payment
        create_transaction(
            db=db,
            transaction_type=TransactionType.LOAN_PAYMENT,
            amount=payment_request.amount,
            description=f"Payment received for loan #{loan.id} - {loan.client.name}",
            seller_id=current_user.id,
            magazine_id=current_user.magazine_id,
            loan_id=loan.id,
            loan_payment_id=payment.id,
            client_id=loan.client_id
        )
        
        db.refresh(payment)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to mark payment as paid: {str(e)}")
    
    return PaymentResponse(
        id=payment.id,
        amount=payment.amount,
        payment_date=payment.payment_date,
        due_date=payment.due_date,
        status=payment.status.value,
        is_late=payment.is_late,
        is_full_payment=payment.is_full_payment,
        loan_id=payment.loan_id
    )

@router.post("/{loan_id}/pay-full", response_model=dict)
def pay_full_loan(
    loan_id: int,
    payment_request: QuickPaymentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Pay the full remaining balance of a loan"""
    # Check if loan exists and user has access
    loan = db.query(Loan).filter(Loan.id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    
    # Check permissions
    if current_user.role != UserRole.ADMIN:
        if loan.magazine_id != current_user.magazine_id:
            raise HTTPException(status_code=403, detail="Access denied")
    
    if loan.is_completed:
        raise HTTPException(status_code=400, detail="Loan is already completed")
    
    # Validate payment amount matches remaining balance
    if abs(payment_request.amount - loan.remaining_amount) > 0.01:  # Allow small floating point differences
        raise HTTPException(
            status_code=400, 
            detail=f"Payment amount ({payment_request.amount}) must match remaining balance ({loan.remaining_amount})"
        )
    
    try:
        # Parse payment date or use current date
        if payment_request.payment_date:
            payment_datetime = datetime.fromisoformat(payment_request.payment_date.replace('Z', '+00:00'))
        else:
            payment_datetime = datetime.now()
        
        # Delete all pending scheduled payments since this is a full payment
        pending_payments = db.query(LoanPayment).filter(
            LoanPayment.loan_id == loan_id,
            LoanPayment.status.in_([PaymentStatus.PENDING, PaymentStatus.OVERDUE])
        ).all()
        
        # Count for response
        payments_count = len(pending_payments)
        
        # Delete pending payments
        for payment in pending_payments:
            db.delete(payment)
        
        # Create a single payment record for the full amount
        full_payment = LoanPayment(
            loan_id=loan_id,
            amount=payment_request.amount,
            due_date=payment_datetime,  # Due date same as payment date for full payments
            payment_date=payment_datetime,
            status=PaymentStatus.PAID,
            is_late=False,
            is_full_payment=True,  # Mark as one-time full payment
            notes="Full loan payment - loan completed in one payment"
        )
        
        db.add(full_payment)
        
        # Complete the loan
        loan.remaining_amount = 0
        loan.is_completed = True
        
        db.commit()
        
        # Create transaction record for full payment
        create_transaction(
            db=db,
            transaction_type=TransactionType.LOAN_PAYMENT,
            amount=payment_request.amount,
            description=f"Full loan payment for loan #{loan.id} - {loan.client.name} (Loan completed)",
            seller_id=current_user.id,
            magazine_id=current_user.magazine_id,
            loan_id=loan.id,
            client_id=loan.client_id
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to pay full loan: {str(e)}")
    
    return {
        "message": "Loan paid in full successfully",
        "loan_id": loan_id,
        "amount_paid": payment_request.amount,
        "payments_settled": payments_count,
        "loan_completed": True
    } 