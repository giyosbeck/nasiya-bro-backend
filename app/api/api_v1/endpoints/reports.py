from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import List, Optional
from datetime import datetime
from app.db.database import get_db
from app.models.transaction import Sale, Loan
from app.models.product import Product
from app.models.user import User, UserRole, Client
from app.api.deps import get_current_user
from pydantic import BaseModel

router = APIRouter()

class ReportsSummary(BaseModel):
    total_amount: float
    sales_count: int
    sales_total: float
    loans_count: int
    loans_total: float
    period_start: str
    period_end: str

class TransactionExport(BaseModel):
    id: int
    type: str
    date: str
    amount: float
    product_name: str
    product_model: str
    client_name: Optional[str]
    seller_name: str
    monthly_payment: Optional[float]
    loan_months: Optional[int]

@router.get("/summary", response_model=ReportsSummary)
def get_reports_summary(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    search: Optional[str] = None,
    transaction_type: Optional[str] = None,  # 'sales', 'loans', or 'all'
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get aggregated summary statistics for reports without pagination"""
    
    # Build base queries
    sales_query = db.query(Sale).join(Product).join(User)
    loans_query = db.query(Loan).join(Product).join(Client).join(User)
    
    # Apply user scope filtering
    if current_user.role != UserRole.ADMIN:
        if not current_user.magazine_id:
            return ReportsSummary(
                total_amount=0, sales_count=0, sales_total=0, 
                loans_count=0, loans_total=0,
                period_start=date_from or "", period_end=date_to or ""
            )
        sales_query = sales_query.filter(Sale.magazine_id == current_user.magazine_id)
        loans_query = loans_query.filter(Loan.magazine_id == current_user.magazine_id)
    
    # Apply date filtering
    if date_from:
        try:
            from_date = datetime.strptime(date_from, "%Y-%m-%d")
            sales_query = sales_query.filter(Sale.sale_date >= from_date)
            loans_query = loans_query.filter(Loan.loan_start_date >= from_date)
        except ValueError:
            pass
    
    if date_to:
        try:
            to_date = datetime.strptime(date_to, "%Y-%m-%d")
            to_date = to_date.replace(hour=23, minute=59, second=59)
            sales_query = sales_query.filter(Sale.sale_date <= to_date)
            loans_query = loans_query.filter(Loan.loan_start_date <= to_date)
        except ValueError:
            pass
    
    # Apply search filtering
    if search:
        search_term = f"%{search}%"
        sales_query = sales_query.filter(
            or_(
                Product.name.ilike(search_term),
                Product.model.ilike(search_term),
                User.name.ilike(search_term)
            )
        )
        loans_query = loans_query.filter(
            or_(
                Product.name.ilike(search_term),
                Product.model.ilike(search_term),
                Client.name.ilike(search_term),
                User.name.ilike(search_term)
            )
        )
    
    # Calculate aggregations based on transaction type filter
    if transaction_type == 'sales':
        # Only sales
        sales_result = sales_query.with_entities(
            func.count(Sale.id).label('count'),
            func.sum(Sale.sale_price).label('total')
        ).first()
        
        sales_count = sales_result.count or 0
        sales_total = float(sales_result.total or 0)
        loans_count = 0
        loans_total = 0.0
        
    elif transaction_type == 'loans':
        # Only loans - calculate total loan amount (initial_payment + monthly_payment * loan_months)
        loans_result = loans_query.with_entities(
            func.count(Loan.id).label('count'),
            func.sum((Loan.initial_payment + (Loan.monthly_payment * Loan.loan_months))).label('total')
        ).first()
        
        sales_count = 0
        sales_total = 0.0
        loans_count = loans_result.count or 0
        loans_total = float(loans_result.total or 0)
        
    else:
        # All transactions
        sales_result = sales_query.with_entities(
            func.count(Sale.id).label('count'),
            func.sum(Sale.sale_price).label('total')
        ).first()
        
        loans_result = loans_query.with_entities(
            func.count(Loan.id).label('count'),
            func.sum((Loan.initial_payment + (Loan.monthly_payment * Loan.loan_months))).label('total')
        ).first()
        
        sales_count = sales_result.count or 0
        sales_total = float(sales_result.total or 0)
        loans_count = loans_result.count or 0
        loans_total = float(loans_result.total or 0)
    
    total_amount = sales_total + loans_total
    
    return ReportsSummary(
        total_amount=total_amount,
        sales_count=sales_count,
        sales_total=sales_total,
        loans_count=loans_count,
        loans_total=loans_total,
        period_start=date_from or "",
        period_end=date_to or ""
    )

@router.get("/export", response_model=List[TransactionExport])
def export_transactions(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    search: Optional[str] = None,
    transaction_type: Optional[str] = None,
    limit: int = 10000,  # Large limit for exports
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Export all filtered transactions for Excel/CSV generation"""
    
    all_transactions = []
    
    # Get sales if needed
    if transaction_type != 'loans':
        sales_query = db.query(Sale).join(Product).join(User)
        
        # Apply user scope
        if current_user.role != UserRole.ADMIN:
            if not current_user.magazine_id:
                pass  # Skip sales
            else:
                sales_query = sales_query.filter(Sale.magazine_id == current_user.magazine_id)
        
        # Apply filters
        if date_from:
            try:
                from_date = datetime.strptime(date_from, "%Y-%m-%d")
                sales_query = sales_query.filter(Sale.sale_date >= from_date)
            except ValueError:
                pass
        
        if date_to:
            try:
                to_date = datetime.strptime(date_to, "%Y-%m-%d")
                to_date = to_date.replace(hour=23, minute=59, second=59)
                sales_query = sales_query.filter(Sale.sale_date <= to_date)
            except ValueError:
                pass
        
        if search:
            search_term = f"%{search}%"
            sales_query = sales_query.filter(
                or_(
                    Product.name.ilike(search_term),
                    Product.model.ilike(search_term),
                    User.name.ilike(search_term)
                )
            )
        
        sales = sales_query.order_by(Sale.created_at.desc()).limit(limit).all()
        
        for sale in sales:
            all_transactions.append(TransactionExport(
                id=sale.id,
                type="sale",
                date=sale.sale_date.strftime("%Y-%m-%d %H:%M:%S"),
                amount=sale.sale_price,
                product_name=sale.product.name,
                product_model=sale.product.model,
                client_name=None,
                seller_name=sale.seller.name,
                monthly_payment=None,
                loan_months=None
            ))
    
    # Get loans if needed
    if transaction_type != 'sales':
        loans_query = db.query(Loan).join(Product).join(Client).join(User)
        
        # Apply user scope
        if current_user.role != UserRole.ADMIN:
            if not current_user.magazine_id:
                pass  # Skip loans
            else:
                loans_query = loans_query.filter(Loan.magazine_id == current_user.magazine_id)
        
        # Apply filters
        if date_from:
            try:
                from_date = datetime.strptime(date_from, "%Y-%m-%d")
                loans_query = loans_query.filter(Loan.loan_start_date >= from_date)
            except ValueError:
                pass
        
        if date_to:
            try:
                to_date = datetime.strptime(date_to, "%Y-%m-%d")
                to_date = to_date.replace(hour=23, minute=59, second=59)
                loans_query = loans_query.filter(Loan.loan_start_date <= to_date)
            except ValueError:
                pass
        
        if search:
            search_term = f"%{search}%"
            loans_query = loans_query.filter(
                or_(
                    Product.name.ilike(search_term),
                    Product.model.ilike(search_term),
                    Client.name.ilike(search_term),
                    User.name.ilike(search_term)
                )
            )
        
        loans = loans_query.order_by(Loan.created_at.desc()).limit(limit).all()
        
        for loan in loans:
            # Calculate total loan amount
            total_amount = (loan.initial_payment or 0) + ((loan.monthly_payment or 0) * (loan.loan_months or 0))
            
            all_transactions.append(TransactionExport(
                id=loan.id,
                type="loan",
                date=loan.loan_start_date.strftime("%Y-%m-%d %H:%M:%S"),
                amount=total_amount,
                product_name=loan.product.name,
                product_model=loan.product.model,
                client_name=loan.client.name,
                seller_name=loan.seller.name,
                monthly_payment=loan.monthly_payment,
                loan_months=loan.loan_months
            ))
    
    # Sort by date descending
    all_transactions.sort(key=lambda x: x.date, reverse=True)
    
    return all_transactions