import pytest
from typing import Generator, Dict
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from datetime import timedelta
import time

from app.db.base import Base
from app.db.base import get_db
from app.main import app
from app.core.config import settings
from app.core.security import get_password_hash, create_access_token
from app.models.user import User
from app.models.product import Product
from app.models.client import Client
from app.services.auth import get_password_hash, create_user_token
from app.models.token import Token
# from app.db.session import engine

# Configuração do banco de dados de teste
SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="function")
def test_user(db: Session):
    try:
        user = User(
            email="test@example.com",
            hashed_password=get_password_hash("testpassword123"),
            full_name="Test User",
            is_active=True,
            is_superuser=False
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"Usuário de teste criado: {user.email}, ID: {user.id}")
        return user
    except Exception as e:
        db.rollback()
        raise e

@pytest.fixture(scope="function")
def test_superuser(db: Session):
    try:
        user = User(
            email="admin@example.com",
            hashed_password=get_password_hash("adminpassword123"),
            full_name="Admin User",
            is_active=True,
            is_superuser=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except Exception as e:
        db.rollback()
        raise e

@pytest.fixture(scope="function")
def test_product(db: Session):
    try:
        # Limpa produtos existentes
        db.query(Product).delete()
        db.commit()
        
        product = Product(
            name="Test Product",
            description="Test Description",
            price=99.99,
            stock=10,
            category="test"
        )
        db.add(product)
        db.commit()
        db.refresh(product)
        return product
    except Exception as e:
        db.rollback()
        raise e

@pytest.fixture(scope="function")
def test_client(db: Session):
    try:
        # Limpa clientes existentes
        db.query(Client).delete()
        db.commit()
        
        # Gera um CPF único usando timestamp
        unique_cpf = f"123456789{int(time.time())}"
        
        client = Client(
            name="Test Client",
            email="client@example.com",
            cpf=unique_cpf,
            phone="11999999999",
            address="Test Address"
        )
        db.add(client)
        db.commit()
        db.refresh(client)
        return client
    except Exception as e:
        db.rollback()
        raise e

@pytest.fixture(scope="function")
def client_dict(test_client: Client):
    return {
        "id": test_client.id,
        "name": test_client.name,
        "email": test_client.email,
        "cpf": test_client.cpf,
        "phone": test_client.phone,
        "address": test_client.address
    }

@pytest.fixture(scope="function")
def user_token_headers(test_user: User, db: Session):
    try:
        # Limpa tokens existentes
        db.query(Token).filter(Token.user_id == test_user.id).delete()
        db.commit()
        
        token = create_user_token(
            db=db,
            user=test_user,
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        print(f"Token gerado e persistido para o usuário: {test_user.email}, Token: {token.token}")
        return {"Authorization": f"Bearer {token.token}"}
    except Exception as e:
        db.rollback()
        raise e

@pytest.fixture(scope="function")
def admin_token_headers(test_superuser: User, db: Session):
    try:
        # Limpa tokens existentes
        db.query(Token).filter(Token.user_id == test_superuser.id).delete()
        db.commit()
        
        token = create_user_token(
            db=db,
            user=test_superuser,
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        print(f"Token gerado e persistido para o admin: {test_superuser.email}, Token: {token.token}")
        return {"Authorization": f"Bearer {token.token}"}
    except Exception as e:
        db.rollback()
        raise e

@pytest.fixture(scope="function")
def product(test_product: Product):
    return {
        "id": test_product.id,
        "name": test_product.name,
        "description": test_product.description,
        "price": test_product.price,
        "stock": test_product.stock,
        "category": test_product.category
    }

@pytest.fixture(scope="session")
def inactive_user(db: Session):
    user = User(
        email="inactive@example.com",
        hashed_password=get_password_hash("testpassword123"),
        full_name="Inactive User",
        is_active=False,
        is_superuser=False
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# NOVO: sobrescrever dependência do banco no app

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db 