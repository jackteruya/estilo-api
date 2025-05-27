import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate

def test_login(client: TestClient, db: Session):
    # Limpa o banco de dados antes do teste
    db.query(User).delete()
    db.commit()
    
    # Registra um usuário
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "testpassword123",
            "full_name": "Test User"
        }
    )
    assert response.status_code == 200
    
    # Tenta fazer login
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "testpassword123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials(client: TestClient, db: Session):
    # Limpa o banco de dados antes do teste
    db.query(User).delete()
    db.commit()
    
    # Registra um usuário
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "testpassword123",
            "full_name": "Test User"
        }
    )
    assert response.status_code == 200
    
    # Tenta fazer login com senha errada
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401
    assert "Credenciais inválidas" in response.json()["detail"]

def test_login_inactive_user(client: TestClient, db: Session):
    # Limpa o banco de dados antes do teste
    db.query(User).delete()
    db.commit()
    
    # Registra um usuário
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "inactive@example.com",
            "password": "testpassword123",
            "full_name": "Inactive User"
        }
    )
    assert response.status_code == 200
    
    # Desativa o usuário
    user = db.query(User).filter(User.email == "inactive@example.com").first()
    user.is_active = False
    db.commit()
    
    # Tenta fazer login
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "inactive@example.com",
            "password": "testpassword123"
        }
    )
    assert response.status_code == 401
    assert "Usuário inativo" in response.json()["detail"]

def test_register(client: TestClient, db: Session):
    # Limpa o banco de dados antes do teste
    db.query(User).delete()
    db.commit()
    
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "testpassword123",
            "full_name": "New User"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["full_name"] == "New User"
    assert "id" in data

def test_register_existing_email(client: TestClient, db: Session):
    # Limpa o banco de dados antes do teste
    db.query(User).delete()
    db.commit()
    
    # Primeiro registro
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "existing@example.com",
            "password": "testpassword123",
            "full_name": "Existing User"
        }
    )
    assert response.status_code == 200
    
    # Tentativa de registro com mesmo email
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "existing@example.com",
            "password": "testpassword123",
            "full_name": "Another User"
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
        "/api/v1/auth/me",
        headers=user_token_headers
    )
    
    assert test_response.status_code == 401
    assert "Token inválido" in test_response.json()["detail"]

def test_login_nonexistent_user(client: TestClient, db: Session):
    # Limpa o banco de dados antes do teste
    db.query(User).delete()
    db.commit()
    
    # Tenta fazer login com usuário inexistente
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "nonexistent@example.com",
            "password": "testpassword123"
        }
    )
    assert response.status_code == 401
    assert "Credenciais inválidas" in response.json()["detail"]

def test_login_expired_token(client: TestClient, db: Session):
    # Limpa o banco de dados antes do teste
    db.query(User).delete()
    db.commit()
    
    # Registra um usuário
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "testpassword123",
            "full_name": "Test User"
        }
    )
    assert response.status_code == 200
    
    # Tenta fazer login com token expirado
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "testpassword123"
        },
        headers={"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyLCJleHAiOjE1MTYyMzkwMjJ9.4Adcj3UFYzPUVaVF43Fm5SWUJNPl0jQzXZxXZxXZxXZ"}
    )
    assert response.status_code == 401
    assert "Token expirado" in response.json()["detail"]

def test_login_malformed_token(client: TestClient, db: Session):
    # Limpa o banco de dados antes do teste
    db.query(User).delete()
    db.commit()
    
    # Registra um usuário
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "testpassword123",
            "full_name": "Test User"
        }
    )
    assert response.status_code == 200
    
    # Tenta fazer login com token mal formatado
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "testpassword123"
        },
        headers={"Authorization": "Bearer malformed_token"}
    )
    assert response.status_code == 401
    assert "Token inválido" in response.json()["detail"]

def test_login_token_without_data(client: TestClient, db: Session):
    # Limpa o banco de dados antes do teste
    db.query(User).delete()
    db.commit()
    
    # Tenta fazer login sem dados
    response = client.post(
        "/api/v1/auth/login",
        data={}
    )
    assert response.status_code == 422
    assert "Field required" in response.json()["detail"][0]["msg"]

def test_login_token_without_version(client: TestClient, db: Session):
    # Limpa o banco de dados antes do teste
    db.query(User).delete()
    db.commit()
    
    # Tenta fazer login sem versão
    response = client.post(
        "/api/auth/login"
    )
    assert response.status_code == 404
    assert "Not Found" in response.json()["detail"]

def test_login_token_without_api_prefix(client: TestClient, db: Session):
    # Limpa o banco de dados antes do teste
    db.query(User).delete()
    db.commit()
    
    # Tenta fazer login sem prefixo de API
    response = client.post(
        "/auth/login"
    )
    assert response.status_code == 404
    assert "Not Found" in response.json()["detail"] 