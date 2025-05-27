import pytest
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.client import Client
from app.schemas.client import ClientCreate, ClientUpdate
from app.services.client import (
    create_client,
    get_client,
    get_clients,
    update_client,
    delete_client
)

def test_create_client(db):
    client_data = ClientCreate(
        name="Test Client",
        email="test@example.com",
        phone="(11) 99999-9999",
        cpf="12345678901",
        address="Test Address"
    )
    client = create_client(db=db, obj_in=client_data)
    assert client.name == client_data.name
    assert client.email == client_data.email
    assert client.phone == client_data.phone
    assert client.cpf == client_data.cpf
    assert client.address == client_data.address

def test_create_client_duplicate_email(db: Session, test_client: Client):
    with pytest.raises(HTTPException) as exc_info:
        create_client(db=db, obj_in=ClientCreate(
            name="Another Client",
            email=test_client.email,
            phone="(11) 88888-8888",
            cpf="98765432100",
            address="Another Address"
        ))
    assert exc_info.value.status_code == 400
    assert "Email já cadastrado" in exc_info.value.detail

def test_create_client_duplicate_cpf(db: Session, test_client: Client):
    with pytest.raises(HTTPException) as exc_info:
        create_client(db=db, obj_in=ClientCreate(
            name="Another Client",
            email="another@example.com",
            cpf=test_client.cpf,
            phone="11999999999",
            address="Another Address"
        ))
    assert exc_info.value.status_code == 400
    assert "CPF já cadastrado" in exc_info.value.detail

def test_get_client(db, test_client):
    client = get_client(db=db, client_id=test_client.id)
    assert client is not None
    assert client.id == test_client.id
    assert client.name == test_client.name
    assert client.email == test_client.email
    assert client.phone == test_client.phone
    assert client.cpf == test_client.cpf
    assert client.address == test_client.address

def test_get_client_not_found(db):
    client = get_client(db=db, client_id=999)
    assert client is None

def test_get_clients(db, test_client):
    clients, total = get_clients(db=db)
    assert total > 0
    assert any(c.id == test_client.id for c in clients)

def test_get_clients_with_search(db, test_client):
    # Cria um cliente adicional para teste de busca
    client_data = ClientCreate(
        name="Search Test",
        email="search@example.com",
        phone="(11) 77777-7777",
        cpf="11122233344",
        address="Search Address"
    )
    create_client(db=db, obj_in=client_data)
    
    # Testa busca por nome
    clients, total = get_clients(db=db, search="Search")
    assert total > 0
    assert any(c.name == "Search Test" for c in clients)
    
    # Testa busca por email
    clients, total = get_clients(db=db, search="search@example.com")
    assert total > 0
    assert any(c.email == "search@example.com" for c in clients)

def test_update_client(db, test_client):
    update_data = ClientUpdate(
        name="Updated Name",
        phone="(11) 77777-7777"
    )
    updated_client = update_client(
        db=db,
        db_obj=test_client,
        obj_in=update_data
    )
    assert updated_client.name == update_data.name
    assert updated_client.phone == update_data.phone
    assert updated_client.email == test_client.email  # Não deve ter mudado
    assert updated_client.cpf == test_client.cpf  # Não deve ter mudado
    assert updated_client.address == test_client.address  # Não deve ter mudado

def test_update_client_not_found(db):
    update_data = ClientUpdate(name="Updated Name")
    with pytest.raises(AttributeError):
        update_client(
            db=db,
            db_obj=None,
            obj_in=update_data
        )

def test_update_client_duplicate_email(db, test_client):
    # Cria outro cliente primeiro
    other_client = ClientCreate(
        name="Other Client",
        email="other@example.com",
        phone="(11) 66666-6666",
        cpf="55566677788",
        address="Other Address"
    )
    create_client(db=db, obj_in=other_client)
    
    # Tenta atualizar o email para um já existente
    update_data = ClientUpdate(name="Test Client", email="other@example.com")
    with pytest.raises(IntegrityError) as exc_info:
        update_client(
            db=db,
            db_obj=test_client,
            obj_in=update_data
        )
    db.rollback()
    assert (
        "UNIQUE constraint failed: clients.email" in str(exc_info.value)
        or "duplicate key value violates unique constraint" in str(exc_info.value)
    )

def test_update_client_duplicate_cpf(db, test_client):
    # Cria outro cliente primeiro com CPF único
    other_client = ClientCreate(
        name="Other Client",
        email="unique_email_for_cpf@example.com",
        phone="(11) 66666-6666",
        cpf="99988877766",  # CPF único
        address="Other Address"
    )
    create_client(db=db, obj_in=other_client)
    
    # Tenta atualizar o CPF para um já existente (do other_client)
    update_data = ClientUpdate(name="Test Client", cpf="99988877766")
    with pytest.raises(IntegrityError) as exc_info:
        update_client(
            db=db,
            db_obj=test_client,
            obj_in=update_data
        )
    db.rollback()
    assert (
        "UNIQUE constraint failed: clients.cpf" in str(exc_info.value)
        or "duplicate key value violates unique constraint" in str(exc_info.value)
    )

def test_delete_client(db, test_client):
    deleted_client = delete_client(db=db, client_id=test_client.id)
    db.rollback()  # Garante que a sessão está limpa para o próximo teste
    assert deleted_client is not None
    assert deleted_client.id == test_client.id
    
    # Verifica se o cliente foi realmente deletado
    client = get_client(db=db, client_id=test_client.id)
    assert client is None

def test_delete_client_not_found(db):
    deleted_client = delete_client(db=db, client_id=999)
    db.rollback()  # Garante que a sessão está limpa para o próximo teste
    assert deleted_client is None 