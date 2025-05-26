import pytest
from typing import Generator, Dict
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.base import get_db
from app.main import app
from app.core.config import settings
from app.core.security import get_password_hash, create_access_token
from app.models.user import User
from app.models.product import Product
from app.models.client import Client
from app.services.auth import get_password_hash
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
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="session")
def test_user(db: Session):
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
    return user

@pytest.fixture(scope="session")
def test_superuser(db: Session):
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

@pytest.fixture(scope="session")
def test_product(db: Session):
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

@pytest.fixture(scope="session")
def test_client(db: Session):
    client = Client(
        name="Test Client",
        email="client@example.com",
        cpf="12345678900",
        phone="11999999999",
        address="Test Address"
    )
    db.add(client)
    db.commit()
    db.refresh(client)
    return client

@pytest.fixture(scope="session")
def user_token_headers(test_user: User):
    access_token = create_access_token(
        subject=str(test_user.id),
        expires_delta=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    return {"Authorization": f"Bearer {access_token}"}

@pytest.fixture(scope="session")
def admin_token_headers(test_superuser: User):
    access_token = create_access_token(
        subject=str(test_superuser.id),
        expires_delta=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    return {"Authorization": f"Bearer {access_token}"} 