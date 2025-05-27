from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from fastapi import HTTPException

from app.models.client import Client
from app.schemas.client import ClientCreate, ClientUpdate


def get_client(db: Session, client_id: int) -> Optional[Client]:
    return db.query(Client).filter(Client.id == client_id).first()


def get_client_by_email(db: Session, email: str) -> Optional[Client]:
    return db.query(Client).filter(Client.email == email).first()


def get_client_by_cpf(db: Session, cpf: str) -> Optional[Client]:
    return db.query(Client).filter(Client.cpf == cpf).first()


def get_clients(
    db: Session,
    page: int = 1,
    size: int = 100,
    search: Optional[str] = None
) -> Tuple[List[Client], int]:
    """
    Retorna uma tupla contendo a lista de clientes e o total de registros.
    """
    query = db.query(Client)
    
    if search:
        search = f"%{search}%"
        query = query.filter(
            or_(
                Client.name.ilike(search),
                Client.email.ilike(search)
            )
        )
    
    # Conta o total de registros
    total = query.count()
    
    # Aplica paginação
    skip = (page - 1) * size
    clients = query.offset(skip).limit(size).all()
    
    return clients, total


def create_client(db: Session, obj_in: ClientCreate) -> Client:
    try:
        # Verifica se já existe um cliente com o mesmo CPF
        existing_client = db.query(Client).filter(Client.cpf == obj_in.cpf).first()
        if existing_client:
            raise HTTPException(
                status_code=400,
                detail="CPF já cadastrado"
            )
        
        # Verifica se já existe um cliente com o mesmo email
        existing_email = db.query(Client).filter(Client.email == obj_in.email).first()
        if existing_email:
            raise HTTPException(
                status_code=400,
                detail="Email já cadastrado"
            )
        
        db_obj = Client(
            name=obj_in.name,
            email=obj_in.email,
            cpf=obj_in.cpf,
            phone=obj_in.phone,
            address=obj_in.address
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


def update_client(
    db: Session,
    *,
    db_obj: Client,
    obj_in: ClientUpdate
) -> Client:
    update_data = obj_in.model_dump(exclude_unset=True)
    
    for field in update_data:
        setattr(db_obj, field, update_data[field])
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_client(db: Session, *, client_id: int) -> Optional[Client]:
    client = db.query(Client).filter(Client.id == client_id).first()
    if client:
        db.delete(client)
        db.commit()
    return client 