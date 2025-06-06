from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    users,
    clients,
    products,
    orders,
    whatsapp
)

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(clients.router, prefix="/clients", tags=["clients"])
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(orders.router, prefix="/orders", tags=["orders"])
api_router.include_router(whatsapp.router, prefix="/whatsapp", tags=["whatsapp"]) 