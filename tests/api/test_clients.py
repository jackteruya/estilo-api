import pytest
from fastapi.testclient import TestClient

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

def test_create_client_duplicate_email(
    client: TestClient,
    user_token_headers: dict
):
    # Primeiro cliente
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
    
    # Tenta criar outro cliente com o mesmo email
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
    assert "Email já registrado" in response.json()["detail"]

def test_create_client_duplicate_cpf(
    client: TestClient,
    user_token_headers: dict
):
    # Primeiro cliente
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
    
    # Tenta criar outro cliente com o mesmo CPF
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
    assert "CPF já registrado" in response.json()["detail"]

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
    create_response = client.post(
        "/api/v1/clients/",
        headers=user_token_headers,
        json={
            "name": "John Doe",
            "email": "john@example.com",
            "cpf": "12345678900",
            "phone": "11999999999"
        }
    )
    
    client_id = create_response.json()["id"]
    
    response = client.get(
        f"/api/v1/clients/{client_id}",
        headers=user_token_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == client_id
    assert data["name"] == "John Doe"
    assert data["email"] == "john@example.com"
    assert data["cpf"] == "12345678900"
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
    create_response = client.post(
        "/api/v1/clients/",
        headers=user_token_headers,
        json={
            "name": "John Doe",
            "email": "john@example.com",
            "cpf": "12345678900",
            "phone": "11999999999"
        }
    )
    
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
    assert data["email"] == "john@example.com"  # Não foi alterado
    assert data["cpf"] == "12345678900"  # Não foi alterado

def test_delete_client(
    client: TestClient,
    user_token_headers: dict
):
    # Cria um cliente
    create_response = client.post(
        "/api/v1/clients/",
        headers=user_token_headers,
        json={
            "name": "John Doe",
            "email": "john@example.com",
            "cpf": "12345678900",
            "phone": "11999999999"
        }
    )
    
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