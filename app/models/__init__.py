from .magazine import Magazine
from .user import User, Client
from .product import Product
from .transaction import Sale, Loan, LoanPayment

__all__ = ["Magazine", "User", "Client", "Product", "Sale", "Loan", "LoanPayment"]