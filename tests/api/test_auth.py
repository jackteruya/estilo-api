import pytest
from fastapi.testclient import TestClient

from app.models.user import User
from app.schemas.user import UserCreate

def test_login(
    client: TestClient,
    test_user: User
):
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user.email,
            "password": "testpassword123"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(
    client: TestClient,
    test_user: User
):
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user.email,
            "password": "wrongpassword"
        }
    )
    
    assert response.status_code == 401
    assert "Credenciais inválidas" in response.json()["detail"]

def test_login_inactive_user(
    client: TestClient,
    admin_token_headers: dict
):
    # Cria um usuário inativo
    create_response = client.post(
        "/api/v1/users/",
        headers=admin_token_headers,
        json={
            "email": "inactive@example.com",
            "password": "testpassword123",
            "full_name": "Inactive User",
            "is_active": False,
            "is_superuser": False
        }
    )
    
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "inactive@example.com",
            "password": "testpassword123"
        }
    )
    
    assert response.status_code == 401
    assert "Usuário inativo" in response.json()["detail"]

def test_register(
    client: TestClient
):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "newpassword123",
            "full_name": "New User"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["full_name"] == "New User"
    assert data["is_active"] is True
    assert data["is_superuser"] is False
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data
    assert "password" not in data

def test_register_existing_email(
    client: TestClient,
    test_user: User
):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": test_user.email,
            "password": "newpassword123",
            "full_name": "New User"
        }
    )
    
    assert response.status_code == 400
    assert "Email já registrado" in response.json()["detail"]

def test_refresh_token(
    client: TestClient,
    test_user: User
):
    # Primeiro faz login para obter o refresh token
    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user.email,
            "password": "testpassword123"
        }
    )
    
    refresh_token = login_response.json()["refresh_token"]
    
    response = client.post(
        "/api/v1/auth/refresh",
        headers={"Authorization": f"Bearer {refresh_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_refresh_token_invalid(
    client: TestClient
):
    response = client.post(
        "/api/v1/auth/refresh",
        headers={"Authorization": "Bearer invalid_token"}
    )
    
    assert response.status_code == 401
    assert "Token inválido" in response.json()["detail"]

def test_logout(
    client: TestClient,
    user_token_headers: dict
):
    response = client.post(
        "/api/v1/auth/logout",
        headers=user_token_headers
    )
    
    assert response.status_code == 200
    assert response.json()["message"] == "Logout realizado com sucesso"
    
    # Tenta usar o token após o logout
    test_response = client.get(
        "/api/v1/users/me",
        headers=user_token_headers
    )
    
    assert test_response.status_code == 401
    assert "Token inválido" in test_response.json()["detail"] 