from fastapi import APIRouter
from app.api.api_v1.endpoints import auth, users, products, auto_products, sales, auto_sales, loans, auto_loans, clients, files, transactions, magazines, reports, notifications

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(magazines.router, prefix="/magazines", tags=["magazines"])
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(auto_products.router, prefix="/auto-products", tags=["auto-products"])
api_router.include_router(sales.router, prefix="/sales", tags=["sales"])
api_router.include_router(auto_sales.router, prefix="/auto-sales", tags=["auto-sales"])
api_router.include_router(loans.router, prefix="/loans", tags=["loans"])
api_router.include_router(auto_loans.router, prefix="/auto-loans", tags=["auto-loans"])
api_router.include_router(clients.router, prefix="/clients", tags=["clients"])
api_router.include_router(files.router, prefix="/files", tags=["files"])
api_router.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])