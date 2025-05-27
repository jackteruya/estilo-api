from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.base import get_db
from app.models.user import User
from app.models.order import OrderStatus
from app.schemas.order import Order, OrderCreate, OrderUpdate
from app.schemas.pagination import PaginatedResponse, PaginationMetadata
from app.services import order as order_service

router = APIRouter()

@router.get("/", response_model=PaginatedResponse[Order])
def read_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1, description="Número da página"),
    size: int = Query(10, ge=1, le=100, description="Quantidade de itens por página"),
    status: OrderStatus = Query(None, description="Filtrar por status do pedido")
) -> Any:
    """
    Listar pedidos com suporte a paginação e filtro por status.
    
    - **page**: Número da página (começa em 1)
    - **size**: Quantidade de itens por página (máximo 100)
    - **status**: Status do pedido para filtrar
    """
    orders, total = order_service.get_orders(
        db=db,
        user_id=current_user.id,
        page=page,
        size=size,
        status=status
    )
    
    # Calcula o total de páginas
    total_pages = (total + size - 1) // size
    
    # Calcula se tem próxima página e página anterior
    has_next = page < total_pages
    has_prev = page > 1
    
    # Calcula os números das páginas
    next_page = page + 1 if has_next else None
    prev_page = page - 1 if has_prev else None
    
    # Cria o objeto de metadados
    metadata = PaginationMetadata(
        total=total,
        page=page,
        size=size,
        pages=total_pages,
        has_next=has_next,
        has_prev=has_prev,
        next_page=next_page,
        prev_page=prev_page
    )
    
    return PaginatedResponse(
        items=orders,
        metadata=metadata
    )

@router.post("/", response_model=Order)
def create_order(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    order_in: OrderCreate
) -> Any:
    """
    Criar novo pedido.
    """
    try:
        order = order_service.create_order(
            db=db,
            user_id=current_user.id,
            obj_in=order_in
        )
        return order
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

@router.get("/{order_id}", response_model=Order)
def read_order(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    order_id: int
) -> Any:
    """
    Obter informações de um pedido específico.
    """
    order = order_service.get_order(db, order_id=order_id)
    if not order:
        raise HTTPException(
            status_code=404,
            detail="Pedido não encontrado."
        )
    if order.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="Você não tem permissão para acessar este pedido."
        )
    return order

@router.put("/{order_id}", response_model=Order)
def update_order(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    order_id: int,
    order_in: OrderUpdate
) -> Any:
    """
    Atualizar status de um pedido.
    """
    order = order_service.get_order(db, order_id=order_id)
    if not order:
        raise HTTPException(
            status_code=404,
            detail="Pedido não encontrado."
        )
    if order.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="Você não tem permissão para atualizar este pedido."
        )
    
    order = order_service.update_order(
        db=db,
        order_id=order_id,
        obj_in=order_in
    )
    return order

@router.delete("/{order_id}", response_model=Order)
def delete_order(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    order_id: int
) -> Any:
    """
    Excluir um pedido.
    """
    order = order_service.get_order(db, order_id=order_id)
    if not order:
        raise HTTPException(
            status_code=404,
            detail="Pedido não encontrado."
        )
    if order.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="Você não tem permissão para excluir este pedido."
        )
    
    order = order_service.delete_order(db=db, order_id=order_id)
    return order 