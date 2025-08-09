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

class RevenueAnalytics(BaseModel):
    total_revenue: float
    total_profit: float
    monthly_recurring_revenue: float
    average_transaction_value: float
    average_profit_margin: float
    direct_sales_revenue: float
    direct_sales_profit: float
    loan_revenue_projected: float
    loan_profit_projected: float
    revenue_growth_percentage: float
    profit_growth_percentage: float
    sales_loan_ratio: float
    collection_rate: float
    total_transactions_count: int
    active_loans_count: int

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

@router.get("/revenue", response_model=RevenueAnalytics)
def get_revenue_analytics(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    search: Optional[str] = None,
    transaction_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed revenue and profit analytics"""
    
    # Build base queries
    sales_query = db.query(Sale).join(Product).join(User)
    loans_query = db.query(Loan).join(Product).join(Client).join(User)
    
    # Apply user scope filtering
    if current_user.role != UserRole.ADMIN:
        if not current_user.magazine_id:
            return RevenueAnalytics(
                total_revenue=0, total_profit=0, monthly_recurring_revenue=0,
                average_transaction_value=0, average_profit_margin=0,
                direct_sales_revenue=0, direct_sales_profit=0,
                loan_revenue_projected=0, loan_profit_projected=0,
                revenue_growth_percentage=0, profit_growth_percentage=0,
                sales_loan_ratio=0, collection_rate=0,
                total_transactions_count=0, active_loans_count=0
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
    
    # Apply transaction type filtering if needed
    include_sales = transaction_type != 'loans'
    include_loans = transaction_type != 'sales'
    
    # Calculate sales analytics
    if include_sales:
        sales = sales_query.all()
        sales_revenue = sum(sale.sale_price for sale in sales)
        sales_profit = sum(
            (sale.sale_price - (sale.product.purchase_price or sale.product.price)) 
            for sale in sales 
            if sale.product.purchase_price is not None
        )
        # Fallback calculation if no purchase_price data
        if sales_profit == 0 and sales_revenue > 0:
            sales_profit = sum(
                (sale.sale_price - sale.product.price * 0.8) 
                for sale in sales
            )
    else:
        sales = []
        sales_revenue = 0
        sales_profit = 0
    
    # Calculate loans analytics
    if include_loans:
        loans = loans_query.all()
        loans_revenue = sum(
            (loan.initial_payment + (loan.monthly_payment * loan.loan_months)) 
            for loan in loans
        )
        loans_profit = sum(
            (loan.initial_payment + (loan.monthly_payment * loan.loan_months)) - 
            (loan.product.purchase_price or loan.product.price)
            for loan in loans 
            if loan.product.purchase_price is not None
        )
        # Fallback calculation
        if loans_profit == 0 and loans_revenue > 0:
            loans_profit = sum(
                (loan.initial_payment + (loan.monthly_payment * loan.loan_months)) - 
                (loan.product.price * 0.8)
                for loan in loans
            )
        monthly_recurring = sum(loan.monthly_payment for loan in loans)
    else:
        loans = []
        loans_revenue = 0
        loans_profit = 0
        monthly_recurring = 0
    
    # Calculate totals
    total_revenue = sales_revenue + loans_revenue
    total_profit = sales_profit + loans_profit
    total_transactions = len(sales) + len(loans)
    
    # Calculate ratios and averages
    average_transaction_value = total_revenue / total_transactions if total_transactions > 0 else 0
    average_profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
    sales_loan_ratio = (len(sales) / len(loans)) if len(loans) > 0 else len(sales)
    
    # Simplified collection rate (could be enhanced with actual payment tracking)
    collection_rate = 85.0  # Placeholder - would need payment tracking data
    
    return RevenueAnalytics(
        total_revenue=float(total_revenue),
        total_profit=float(total_profit),
        monthly_recurring_revenue=float(monthly_recurring),
        average_transaction_value=float(average_transaction_value),
        average_profit_margin=float(average_profit_margin),
        direct_sales_revenue=float(sales_revenue),
        direct_sales_profit=float(sales_profit),
        loan_revenue_projected=float(loans_revenue),
        loan_profit_projected=float(loans_profit),
        revenue_growth_percentage=0.0,  # Would need previous period data
        profit_growth_percentage=0.0,   # Would need previous period data
        sales_loan_ratio=float(sales_loan_ratio),
        collection_rate=float(collection_rate),
        total_transactions_count=total_transactions,
        active_loans_count=len(loans)
    )