from fastapi import APIRouter
from app.api.api_v1.endpoints import auth, users, products, sales, loans, clients, files, transactions, magazines

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(magazines.router, prefix="/magazines", tags=["magazines"])
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(sales.router, prefix="/sales", tags=["sales"])
api_router.include_router(loans.router, prefix="/loans", tags=["loans"])
api_router.include_router(clients.router, prefix="/clients", tags=["clients"])
api_router.include_router(files.router, prefix="/files", tags=["files"])
api_router.include_router(transactions.router, prefix="/transactions", tags=["transactions"]) 