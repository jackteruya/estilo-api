from fastapi import APIRouter

from app.api.v1.endpoints import auth, clients, products, orders
# , clients, products, orders)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["autenticação"])
api_router.include_router(clients.router, prefix="/clients", tags=["clientes"])
api_router.include_router(products.router, prefix="/products", tags=["produtos"])
api_router.include_router(orders.router, prefix="/orders", tags=["pedidos"])