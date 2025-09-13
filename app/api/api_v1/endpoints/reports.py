from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import List, Optional
from datetime import datetime
from app.db.database import get_db
from app.models.transaction import Sale, Loan
from app.models.auto_transaction import AutoSale, AutoLoan
from app.models.product import Product
from app.models.auto_product import AutoProduct
from app.models.user import User, UserRole, UserType, Client
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
    
    # Check user type and build appropriate queries
    is_auto_user = current_user.user_type == UserType.AUTO
    
    if is_auto_user:
        # Build auto queries
        sales_query = db.query(AutoSale).join(AutoProduct).join(User)
        loans_query = db.query(AutoLoan).join(AutoProduct).join(Client).join(User)
    else:
        # Build regular queries
        sales_query = db.query(Sale).join(Product).join(User)
        loans_query = db.query(Loan).join(Product).join(Client).join(User)
    
    # Apply user scope filtering
    if current_user.role != UserRole.ADMIN:
        if is_auto_user:
            # AUTO users: Filter by seller_id (individual business)
            sales_query = sales_query.filter(AutoSale.seller_id == current_user.id)
            loans_query = loans_query.filter(AutoLoan.seller_id == current_user.id)
        else:
            # GADGETS users: Filter by magazine_id (shared business)
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
            if is_auto_user:
                sales_query = sales_query.filter(AutoSale.sale_date >= from_date)
                loans_query = loans_query.filter(AutoLoan.loan_start_date >= from_date)
            else:
                sales_query = sales_query.filter(Sale.sale_date >= from_date)
                loans_query = loans_query.filter(Loan.loan_start_date >= from_date)
        except ValueError:
            pass
    
    if date_to:
        try:
            to_date = datetime.strptime(date_to, "%Y-%m-%d")
            to_date = to_date.replace(hour=23, minute=59, second=59)
            if is_auto_user:
                sales_query = sales_query.filter(AutoSale.sale_date <= to_date)
                loans_query = loans_query.filter(AutoLoan.loan_start_date <= to_date)
            else:
                sales_query = sales_query.filter(Sale.sale_date <= to_date)
                loans_query = loans_query.filter(Loan.loan_start_date <= to_date)
        except ValueError:
            pass
    
    # Apply search filtering
    if search:
        search_term = f"%{search}%"
        if is_auto_user:
            sales_query = sales_query.filter(
                or_(
                    AutoProduct.car_name.ilike(search_term),
                    AutoProduct.model.ilike(search_term),
                    AutoProduct.color.ilike(search_term),
                    User.name.ilike(search_term)
                )
            )
            loans_query = loans_query.filter(
                or_(
                    AutoProduct.car_name.ilike(search_term),
                    AutoProduct.model.ilike(search_term),
                    AutoProduct.color.ilike(search_term),
                    Client.name.ilike(search_term),
                    User.name.ilike(search_term)
                )
            )
        else:
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
        if is_auto_user:
            sales_result = sales_query.with_entities(
                func.count(AutoSale.id).label('count'),
                func.sum(AutoSale.sale_price).label('total')
            ).first()
        else:
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
        if is_auto_user:
            loans_result = loans_query.with_entities(
                func.count(AutoLoan.id).label('count'),
                func.sum((AutoLoan.initial_payment + (AutoLoan.monthly_payment * AutoLoan.loan_months))).label('total')
            ).first()
        else:
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
        if is_auto_user:
            sales_result = sales_query.with_entities(
                func.count(AutoSale.id).label('count'),
                func.sum(AutoSale.sale_price).label('total')
            ).first()
            
            loans_result = loans_query.with_entities(
                func.count(AutoLoan.id).label('count'),
                func.sum((AutoLoan.initial_payment + (AutoLoan.monthly_payment * AutoLoan.loan_months))).label('total')
            ).first()
        else:
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
    is_auto_user = current_user.user_type == UserType.AUTO
    
    # Get sales if needed
    if transaction_type != 'loans':
        if is_auto_user:
            sales_query = db.query(AutoSale)
        else:
            sales_query = db.query(Sale)
        
        # Apply user scope
        if current_user.role != UserRole.ADMIN:
            if not current_user.magazine_id:
                pass  # Skip sales
            else:
                if is_auto_user:
                    sales_query = sales_query.filter(AutoSale.magazine_id == current_user.magazine_id)
                else:
                    sales_query = sales_query.filter(Sale.magazine_id == current_user.magazine_id)
        
        # Apply filters
        if date_from:
            try:
                from_date = datetime.strptime(date_from, "%Y-%m-%d")
                if is_auto_user:
                    sales_query = sales_query.filter(AutoSale.sale_date >= from_date)
                else:
                    sales_query = sales_query.filter(Sale.sale_date >= from_date)
            except ValueError:
                pass
        
        if date_to:
            try:
                to_date = datetime.strptime(date_to, "%Y-%m-%d")
                to_date = to_date.replace(hour=23, minute=59, second=59)
                if is_auto_user:
                    sales_query = sales_query.filter(AutoSale.sale_date <= to_date)
                else:
                    sales_query = sales_query.filter(Sale.sale_date <= to_date)
            except ValueError:
                pass
        
        # Skip search filtering for now to debug the core issue
        # if search:
        #     search_term = f"%{search}%"
        
        if is_auto_user:
            sales = sales_query.order_by(AutoSale.created_at.desc()).limit(limit).all()
            
            for sale in sales:
                all_transactions.append(TransactionExport(
                    id=sale.id,
                    type="sale",
                    date=sale.sale_date.strftime("%Y-%m-%d %H:%M:%S"),
                    amount=sale.sale_price,
                    product_name=sale.auto_product.car_name,
                    product_model=f"{sale.auto_product.model} • {sale.auto_product.color} • {sale.auto_product.year}",
                    client_name=None,
                    seller_name=sale.seller.name,
                    monthly_payment=None,
                    loan_months=None
                ))
        else:
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
        if is_auto_user:
            loans_query = db.query(AutoLoan)
        else:
            loans_query = db.query(Loan)
        
        # Apply user scope
        if current_user.role != UserRole.ADMIN:
            if not current_user.magazine_id:
                pass  # Skip loans
            else:
                if is_auto_user:
                    loans_query = loans_query.filter(AutoLoan.magazine_id == current_user.magazine_id)
                else:
                    loans_query = loans_query.filter(Loan.magazine_id == current_user.magazine_id)
        
        # Apply filters
        if date_from:
            try:
                from_date = datetime.strptime(date_from, "%Y-%m-%d")
                if is_auto_user:
                    loans_query = loans_query.filter(AutoLoan.loan_start_date >= from_date)
                else:
                    loans_query = loans_query.filter(Loan.loan_start_date >= from_date)
            except ValueError:
                pass
        
        if date_to:
            try:
                to_date = datetime.strptime(date_to, "%Y-%m-%d")
                to_date = to_date.replace(hour=23, minute=59, second=59)
                if is_auto_user:
                    loans_query = loans_query.filter(AutoLoan.loan_start_date <= to_date)
                else:
                    loans_query = loans_query.filter(Loan.loan_start_date <= to_date)
            except ValueError:
                pass
        
        # Skip search filtering for now to debug the core issue  
        # if search:
        #     search_term = f"%{search}%"
        
        if is_auto_user:
            loans = loans_query.order_by(AutoLoan.created_at.desc()).limit(limit).all()
            
            for loan in loans:
                # Calculate total loan amount
                total_amount = (loan.initial_payment or 0) + ((loan.monthly_payment or 0) * (loan.loan_months or 0))
                
                all_transactions.append(TransactionExport(
                    id=loan.id,
                    type="loan",
                    date=loan.loan_start_date.strftime("%Y-%m-%d %H:%M:%S"),
                    amount=total_amount,
                    product_name=loan.auto_product.car_name,
                    product_model=f"{loan.auto_product.model} • {loan.auto_product.color} • {loan.auto_product.year}",
                    client_name=loan.client.name,
                    seller_name=loan.seller.name,
                    monthly_payment=loan.monthly_payment,
                    loan_months=loan.loan_months
                ))
        else:
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
    
    # Check user type and build appropriate queries
    is_auto_user = current_user.user_type == UserType.AUTO
    
    if is_auto_user:
        # Build auto queries
        sales_query = db.query(AutoSale).join(AutoProduct).join(User)
        loans_query = db.query(AutoLoan).join(AutoProduct).join(Client).join(User)
    else:
        # Build regular queries
        sales_query = db.query(Sale).join(Product).join(User)
        loans_query = db.query(Loan).join(Product).join(Client).join(User)
    
    # Apply user scope filtering
    if current_user.role != UserRole.ADMIN:
        if is_auto_user:
            # AUTO users: Filter by seller_id (individual business)
            sales_query = sales_query.filter(AutoSale.seller_id == current_user.id)
            loans_query = loans_query.filter(AutoLoan.seller_id == current_user.id)
        else:
            # GADGETS users: Filter by magazine_id (shared business)
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
            if is_auto_user:
                sales_query = sales_query.filter(AutoSale.sale_date >= from_date)
                loans_query = loans_query.filter(AutoLoan.loan_start_date >= from_date)
            else:
                sales_query = sales_query.filter(Sale.sale_date >= from_date)
                loans_query = loans_query.filter(Loan.loan_start_date >= from_date)
        except ValueError:
            pass
    
    if date_to:
        try:
            to_date = datetime.strptime(date_to, "%Y-%m-%d")
            to_date = to_date.replace(hour=23, minute=59, second=59)
            if is_auto_user:
                sales_query = sales_query.filter(AutoSale.sale_date <= to_date)
                loans_query = loans_query.filter(AutoLoan.loan_start_date <= to_date)
            else:
                sales_query = sales_query.filter(Sale.sale_date <= to_date)
                loans_query = loans_query.filter(Loan.loan_start_date <= to_date)
        except ValueError:
            pass
    
    # Apply search filtering
    if search:
        search_term = f"%{search}%"
        if is_auto_user:
            sales_query = sales_query.filter(
                or_(
                    AutoProduct.car_name.ilike(search_term),
                    AutoProduct.model.ilike(search_term),
                    AutoProduct.color.ilike(search_term),
                    User.name.ilike(search_term)
                )
            )
            loans_query = loans_query.filter(
                or_(
                    AutoProduct.car_name.ilike(search_term),
                    AutoProduct.model.ilike(search_term),
                    AutoProduct.color.ilike(search_term),
                    Client.name.ilike(search_term),
                    User.name.ilike(search_term)
                )
            )
        else:
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
        
        if is_auto_user:
            # For AUTO sales, use auto_product relationship
            sales_profit = sum(
                (sale.sale_price - (sale.auto_product.purchase_price or sale.auto_product.sale_price)) 
                for sale in sales 
                if hasattr(sale.auto_product, 'purchase_price') and sale.auto_product.purchase_price is not None
            )
            # Fallback calculation if no purchase_price data
            if sales_profit == 0 and sales_revenue > 0:
                sales_profit = sum(
                    (sale.sale_price - sale.auto_product.sale_price * 0.8) 
                    for sale in sales
                )
        else:
            # For regular sales, use product relationship
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
        
        if is_auto_user:
            # For AUTO loans, use auto_product relationship
            loans_profit = sum(
                (loan.initial_payment + (loan.monthly_payment * loan.loan_months)) - 
                (loan.auto_product.purchase_price or loan.auto_product.sale_price)
                for loan in loans 
                if hasattr(loan.auto_product, 'purchase_price') and loan.auto_product.purchase_price is not None
            )
            # Fallback calculation
            if loans_profit == 0 and loans_revenue > 0:
                loans_profit = sum(
                    (loan.initial_payment + (loan.monthly_payment * loan.loan_months)) - 
                    (loan.auto_product.sale_price * 0.8)
                    for loan in loans
                )
        else:
            # For regular loans, use product relationship
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