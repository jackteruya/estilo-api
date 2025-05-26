import pytest
from datetime import timedelta
from jose import jwt

from app.core.config import settings
from app.core.security import create_access_token, verify_password
from app.api.deps import get_current_user, get_current_active_superuser
from app.services.auth import (
    authenticate
)
from app.models.user import User

def test_authenticate_user(db, test_user):
    user = authenticate(db, test_user.email, "testpassword123")
    assert user is not None
    assert user.email == test_user.email
    assert verify_password("testpassword123", user.hashed_password)

def test_authenticate_user_wrong_password(db, test_user):
    user = authenticate(db, test_user.email, "wrongpassword")
    assert user is False

def test_authenticate_user_wrong_email(db):
    user = authenticate(db, "wrong@example.com", "testpassword123")
    assert user is False

def test_get_current_user(db, test_user):
    access_token = create_access_token(
        subject=str(test_user.id),
        expires_delta=timedelta(minutes=15)
    )
    
    user = get_current_user(db, access_token)
    assert user is not None
    assert user.id == test_user.id
    assert user.email == test_user.email

def test_get_current_user_invalid_token(db):
    user = get_current_user(db, "invalid_token")
    assert user is None

def test_get_current_active_user(db, test_user):
    access_token = create_access_token(
        subject=str(test_user.id),
        expires_delta=timedelta(minutes=15)
    )
    
    user = get_current_user(db, access_token)
    assert user is not None
    assert user.id == test_user.id
    assert user.is_active is True

def test_get_current_active_user_inactive(db):
    # Cria um usuário inativo
    inactive_user = User(
        email="inactive@example.com",
        hashed_password="hashed_password",
        full_name="Inactive User",
        is_active=False
    )
    db.add(inactive_user)
    db.commit()
    db.refresh(inactive_user)
    
    access_token = create_access_token(
        subject=str(inactive_user.id),
        expires_delta=timedelta(minutes=15)
    )
    
    with pytest.raises(Exception) as exc_info:
        get_current_user(db, access_token)
    assert "Usuário inativo" in str(exc_info.value)

def test_get_current_active_superuser(db, test_superuser):
    access_token = create_access_token(
        subject=str(test_superuser.id),
        expires_delta=timedelta(minutes=15)
    )
    
    user = get_current_active_superuser(db, access_token)
    assert user is not None
    assert user.id == test_superuser.id
    assert user.is_superuser is True

def test_get_current_active_superuser_not_superuser(db, test_user):
    access_token = create_access_token(
        subject=str(test_user.id),
        expires_delta=timedelta(minutes=15)
    )
    
    with pytest.raises(Exception) as exc_info:
        get_current_active_superuser(db, access_token)
    assert "Permissão negada" in str(exc_info.value) 