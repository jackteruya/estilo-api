from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.base import get_db
from app.models.user import User
from app.schemas.client import Client, ClientCreate, ClientUpdate
from app.schemas.pagination import PaginatedResponse, PaginationMetadata
from app.services import client as client_service

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[Client])
def read_clients(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1, description="Número da página"),
    size: int = Query(10, ge=1, le=100, description="Quantidade de itens por página"),
    search: str = Query(None, min_length=1, description="Termo de busca (nome ou email)")
) -> Any:
    """
    Listar clientes com suporte a paginação e busca por nome/email.
    
    - **page**: Número da página (começa em 1)
    - **size**: Quantidade de itens por página (máximo 100)
    - **search**: Termo de busca para filtrar por nome ou email
    """
    clients, total = client_service.get_clients(
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
        items=clients,
        metadata=metadata
    )


@router.post("/", response_model=Client)
def create_client(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    client_in: ClientCreate
) -> Any:
    """
    Criar novo cliente.
    """
    # Verificar se já existe cliente com o mesmo email
    client = client_service.get_client_by_email(db, email=client_in.email)
    if client:
        raise HTTPException(
            status_code=400,
            detail="Já existe um cliente cadastrado com este email."
        )
    
    # Verificar se já existe cliente com o mesmo CPF
    client = client_service.get_client_by_cpf(db, cpf=client_in.cpf)
    if client:
        raise HTTPException(
            status_code=400,
            detail="Já existe um cliente cadastrado com este CPF."
        )
    
    client = client_service.create_client(db=db, obj_in=client_in)
    return client


@router.get("/{client_id}", response_model=Client)
def read_client(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    client_id: int
) -> Any:
    """
    Obter informações de um cliente específico.
    """
    client = client_service.get_client(db, client_id=client_id)
    if not client:
        raise HTTPException(
            status_code=404,
            detail="Cliente não encontrado."
        )
    return client


@router.put("/{client_id}", response_model=Client)
def update_client(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    client_id: int,
    client_in: ClientUpdate
) -> Any:
    """
    Atualizar informações de um cliente específico.
    """
    client = client_service.get_client(db, client_id=client_id)
    if not client:
        raise HTTPException(
            status_code=404,
            detail="Cliente não encontrado."
        )
    
    # Se estiver atualizando email, verificar se já existe
    if client_in.email and client_in.email != client.email:
        existing_client = client_service.get_client_by_email(db, email=client_in.email)
        if existing_client:
            raise HTTPException(
                status_code=400,
                detail="Já existe um cliente cadastrado com este email."
            )
    
    # Se estiver atualizando CPF, verificar se já existe
    if client_in.cpf and client_in.cpf != client.cpf:
        existing_client = client_service.get_client_by_cpf(db, cpf=client_in.cpf)
        if existing_client:
            raise HTTPException(
                status_code=400,
                detail="Já existe um cliente cadastrado com este CPF."
            )
    
    client = client_service.update_client(
        db=db,
        db_obj=client,
        obj_in=client_in
    )
    return client


@router.delete("/{client_id}", response_model=Client)
def delete_client(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    client_id: int
) -> Any:
    """
    Excluir um cliente.
    """
    client = client_service.get_client(db, client_id=client_id)
    if not client:
        raise HTTPException(
            status_code=404,
            detail="Cliente não encontrado."
        )
    
    client = client_service.delete_client(db=db, client_id=client_id)
    return client 