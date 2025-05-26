from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.base import get_db
from app.models.user import User
from app.schemas.product import Product, ProductCreate, ProductUpdate
from app.schemas.pagination import PaginatedResponse, PaginationMetadata
from app.services import product as product_service

router = APIRouter()

@router.get("/", response_model=PaginatedResponse[Product])
def read_products(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1, description="Número da página"),
    size: int = Query(10, ge=1, le=100, description="Quantidade de itens por página"),
    search: str = Query(None, min_length=1, description="Termo de busca (nome ou descrição)")
) -> Any:
    """
    Listar produtos com suporte a paginação e busca por nome/descrição.
    
    - **page**: Número da página (começa em 1)
    - **size**: Quantidade de itens por página (máximo 100)
    - **search**: Termo de busca para filtrar por nome ou descrição
    """
    products, total = product_service.get_products(
        db=db,
        page=page,
        size=size,
        search=search
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
        items=products,
        metadata=metadata
    )

@router.post("/", response_model=Product)
def create_product(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    product_in: ProductCreate
) -> Any:
    """
    Criar novo produto.
    """
    product = product_service.create_product(db=db, obj_in=product_in)
    return product

@router.get("/{product_id}", response_model=Product)
def read_product(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    product_id: int
) -> Any:
    """
    Obter informações de um produto específico.
    """
    product = product_service.get_product(db, product_id=product_id)
    if not product:
        raise HTTPException(
            status_code=404,
            detail="Produto não encontrado."
        )
    return product

@router.put("/{product_id}", response_model=Product)
def update_product(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    product_id: int,
    product_in: ProductUpdate
) -> Any:
    """
    Atualizar informações de um produto específico.
    """
    product = product_service.get_product(db, product_id=product_id)
    if not product:
        raise HTTPException(
            status_code=404,
            detail="Produto não encontrado."
        )
    
    product = product_service.update_product(
        db=db,
        db_obj=product,
        obj_in=product_in
    )
    return product

@router.delete("/{product_id}", response_model=Product)
def delete_product(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    product_id: int
) -> Any:
    """
    Excluir um produto.
    """
    product = product_service.get_product(db, product_id=product_id)
    if not product:
        raise HTTPException(
            status_code=404,
            detail="Produto não encontrado."
        )
    
    product = product_service.delete_product(db=db, product_id=product_id)
    return product 