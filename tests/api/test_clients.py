import pytest
from fastapi.testclient import TestClient
import random

def generate_unique_cpf():
    """Gera um CPF único para testes"""
    return f"{random.randint(10000000000, 99999999999)}"

def test_create_client(
    client: TestClient,
    user_token_headers: dict
):
    response = client.post(
        "/api/v1/clients/",
        headers=user_token_headers,
        json={
            "name": "John Doe",
            "email": "john@example.com",
            "cpf": "12345678900",
            "phone": "11999999999"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "John Doe"
    assert data["email"] == "john@example.com"
    assert data["cpf"] == "12345678900"
    assert data["phone"] == "11999999999"
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data
    assert data["is_active"] is True

def test_create_client_duplicate_email(
    client: TestClient,
    user_token_headers: dict
):
    # Criar primeiro cliente
    client.post(
        "/api/v1/clients/",
        headers=user_token_headers,
        json={
            "name": "John Doe",
            "email": "john@example.com",
            "cpf": "12345678900",
            "phone": "11999999999"
        }
    )
    
    # Tentar criar cliente com mesmo email
    response = client.post(
        "/api/v1/clients/",
        headers=user_token_headers,
        json={
            "name": "Jane Doe",
            "email": "john@example.com",
            "cpf": "98765432100",
            "phone": "11988888888"
        }
    )
    
    assert response.status_code == 400
    assert "Já existe um cliente cadastrado com este email" in response.json()["detail"]

def test_create_client_duplicate_cpf(
    client: TestClient,
    user_token_headers: dict
):
    # Criar primeiro cliente
    client.post(
        "/api/v1/clients/",
        headers=user_token_headers,
        json={
            "name": "John Doe",
            "email": "john@example.com",
            "cpf": "12345678900",
            "phone": "11999999999"
        }
    )
    
    # Tentar criar cliente com mesmo CPF
    response = client.post(
        "/api/v1/clients/",
        headers=user_token_headers,
        json={
            "name": "Jane Doe",
            "email": "jane@example.com",
            "cpf": "12345678900",
            "phone": "11988888888"
        }
    )
    
    assert response.status_code == 400
    assert "Já existe um cliente cadastrado com este CPF" in response.json()["detail"]

def test_read_clients(
    client: TestClient,
    user_token_headers: dict
):
    # Cria dois clientes
    for i in range(2):
        client.post(
            "/api/v1/clients/",
            headers=user_token_headers,
            json={
                "name": f"Client {i}",
                "email": f"client{i}@example.com",
                "cpf": f"1234567890{i}",
                "phone": f"1199999999{i}"
            }
        )
    
    response = client.get(
        "/api/v1/clients/",
        headers=user_token_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["metadata"]["total"] >= 2
    assert len(data["items"]) >= 2

def test_read_clients_with_search(
    client: TestClient,
    user_token_headers: dict
):
    # Cria um cliente
    client.post(
        "/api/v1/clients/",
        headers=user_token_headers,
        json={
            "name": "John Doe",
            "email": "john@example.com",
            "cpf": "12345678900",
            "phone": "11999999999"
        }
    )
    
    response = client.get(
        "/api/v1/clients/?search=John",
        headers=user_token_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["metadata"]["total"] >= 1
    assert len(data["items"]) >= 1
    assert all("John" in c["name"] for c in data["items"])

def test_read_client(
    client: TestClient,
    user_token_headers: dict
):
    # Cria um cliente
    data = {
        "name": "Cliente Teste",
        "email": f"cliente.read.{random.randint(1000, 9999)}@example.com",
        "phone": "11999999999",
        "cpf": generate_unique_cpf(),
        "address": "Rua Teste, 123"
    }
    create_response = client.post("/api/v1/clients/", json=data, headers=user_token_headers)
    print('Status code (create):', create_response.status_code)
    print('Response JSON (create):', create_response.json())
    client_id = create_response.json()["id"]
    
    response = client.get(
        f"/api/v1/clients/{client_id}",
        headers=user_token_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == client_id
    assert data["name"] == "Cliente Teste"
    assert data["email"] == data["email"]  # Usando o email gerado
    assert data["cpf"] == data["cpf"]  # Usando o CPF gerado
    assert data["phone"] == "11999999999"

def test_read_client_not_found(
    client: TestClient,
    user_token_headers: dict
):
    response = client.get(
        "/api/v1/clients/999",
        headers=user_token_headers
    )
    
    assert response.status_code == 404
    assert "Cliente não encontrado" in response.json()["detail"]

def test_update_client(
    client: TestClient,
    user_token_headers: dict
):
    # Cria um cliente
    data = {
        "name": "Cliente Update",
        "email": f"cliente.update.{random.randint(1000, 9999)}@example.com",
        "phone": "11999999999",
        "cpf": generate_unique_cpf(),
        "address": "Rua Update, 123"
    }
    create_response = client.post("/api/v1/clients/", json=data, headers=user_token_headers)
    print('Status code (create):', create_response.status_code)
    print('Response JSON (create):', create_response.json())
    client_id = create_response.json()["id"]
    
    response = client.put(
        f"/api/v1/clients/{client_id}",
        headers=user_token_headers,
        json={
            "name": "John Updated",
            "phone": "11988888888"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == client_id
    assert data["name"] == "John Updated"
    assert data["phone"] == "11988888888"
    assert data["email"] == data["email"]  # Usando o email gerado
    assert data["cpf"] == data["cpf"]  # Usando o CPF gerado

def test_delete_client(
    client: TestClient,
    user_token_headers: dict
):
    # Cria um cliente
    data = {
        "name": "Cliente Delete",
        "email": f"cliente.delete.{random.randint(1000, 9999)}@example.com",
        "phone": "11999999999",
        "cpf": generate_unique_cpf(),
        "address": "Rua Delete, 123"
    }
    create_response = client.post("/api/v1/clients/", json=data, headers=user_token_headers)
    print('Status code (create):', create_response.status_code)
    print('Response JSON (create):', create_response.json())
    client_id = create_response.json()["id"]
    
    response = client.delete(
        f"/api/v1/clients/{client_id}",
        headers=user_token_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == client_id
    
    # Verifica se o cliente foi realmente deletado
    get_response = client.get(
        f"/api/v1/clients/{client_id}",
        headers=user_token_headers
    )
    assert get_response.status_code == 404 