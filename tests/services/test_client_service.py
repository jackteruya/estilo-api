import pytest
from sqlalchemy.orm import Session

from app.services.client import (
    create_client,
    get_client,
    get_clients,
    update_client,
    delete_client
)
from app.models.client import Client
from app.schemas.client import ClientCreate, ClientUpdate

def test_create_client(db: Session):
    client_data = ClientCreate(
        name="New Client",
        email="new@example.com",
        cpf="12345678900",
        phone="11999999999",
        address="New Address"
    )
    client = create_client(db, client_data)
    assert client.name == client_data.name
    assert client.email == client_data.email
    assert client.cpf == client_data.cpf

def test_create_client_duplicate_email(db: Session, test_client: Client):
    client_data = ClientCreate(
        name="Another Client",
        email=test_client.email,  # Email duplicado
        phone="(11) 88888-8888",
        cpf="987.654.321-00",
        address="Another Address",
        city="Another City",
        state="AS",
        zip_code="87654-321"
    )
    
    with pytest.raises(Exception) as exc_info:
        create_client(db, client_data)
    assert "Email já registrado" in str(exc_info.value)

def test_create_client_duplicate_cpf(db: Session, test_client: Client):
    client_data = ClientCreate(
        name="Another Client",
        email="another@example.com",
        phone="(11) 88888-8888",
        cpf=test_client.cpf,  # CPF duplicado
        address="Another Address",
        city="Another City",
        state="AS",
        zip_code="87654-321"
    )
    
    with pytest.raises(Exception) as exc_info:
        create_client(db, client_data)
    assert "CPF já registrado" in str(exc_info.value)

def test_get_client(db: Session, test_client: Client):
    client = get_client(db, test_client.id)
    assert client is not None
    assert client.id == test_client.id
    assert client.name == test_client.name
    assert client.email == test_client.email
    assert client.phone == test_client.phone
    assert client.cpf == test_client.cpf
    assert client.address == test_client.address
    assert client.city == test_client.city
    assert client.state == test_client.state
    assert client.zip_code == test_client.zip_code

def test_get_client_not_found(db: Session):
    client = get_client(db, 999)
    assert client is None

def test_get_clients(db: Session, test_client: Client):
    clients = get_clients(db)
    assert len(clients) >= 1
    assert any(c.id == test_client.id for c in clients)

def test_get_clients_with_search(db: Session):
    client_data = ClientCreate(
        name="Search Client",
        email="search@example.com",
        cpf="11122233344",
        phone="11999999999",
        address="Search Address"
    )
    create_client(db, client_data)
    clients = get_clients(db, search="Search")
    assert len(clients) > 0
    assert any(c.name == "Search Client" for c in clients)

def test_update_client(db: Session, test_client: Client):
    update_data = ClientUpdate(
        name="Updated Client",
        phone="(11) 66666-6666",
        address="Updated Address"
    )
    
    updated_client = update_client(db, test_client.id, update_data)
    assert updated_client is not None
    assert updated_client.id == test_client.id
    assert updated_client.name == update_data.name
    assert updated_client.phone == update_data.phone
    assert updated_client.address == update_data.address
    assert updated_client.email == test_client.email  # Não foi alterado
    assert updated_client.cpf == test_client.cpf  # Não foi alterado
    assert updated_client.city == test_client.city  # Não foi alterado
    assert updated_client.state == test_client.state  # Não foi alterado
    assert updated_client.zip_code == test_client.zip_code  # Não foi alterado

def test_update_client_not_found(db: Session):
    update_data = ClientUpdate(
        name="Updated Client"
    )
    
    updated_client = update_client(db, 999, update_data)
    assert updated_client is None

def test_update_client_duplicate_email(db: Session, test_client: Client):
    # Cria outro cliente
    other_client = create_client(
        db,
        ClientCreate(
            name="Other Client",
            email="other@example.com",
            phone="(11) 55555-5555",
            cpf="555.666.777-88",
            address="Other Address",
            city="Other City",
            state="OS",
            zip_code="55555-666"
        )
    )
    
    # Tenta atualizar o email para um já existente
    update_data = ClientUpdate(
        email=test_client.email
    )
    
    with pytest.raises(Exception) as exc_info:
        update_client(db, other_client.id, update_data)
    assert "Email já registrado" in str(exc_info.value)

def test_update_client_duplicate_cpf(db: Session, test_client: Client):
    # Cria outro cliente
    other_client = create_client(
        db,
        ClientCreate(
            name="Other Client",
            email="other@example.com",
            phone="(11) 55555-5555",
            cpf="555.666.777-88",
            address="Other Address",
            city="Other City",
            state="OS",
            zip_code="55555-666"
        )
    )
    
    # Tenta atualizar o CPF para um já existente
    update_data = ClientUpdate(
        cpf=test_client.cpf
    )
    
    with pytest.raises(Exception) as exc_info:
        update_client(db, other_client.id, update_data)
    assert "CPF já registrado" in str(exc_info.value)

def test_delete_client(db: Session, test_client: Client):
    deleted_client = delete_client(db, test_client.id)
    assert deleted_client is not None
    assert deleted_client.id == test_client.id
    
    # Verifica se o cliente foi realmente deletado
    client = get_client(db, test_client.id)
    assert client is None

def test_delete_client_not_found(db: Session):
    deleted_client = delete_client(db, 999)
    assert deleted_client is None 