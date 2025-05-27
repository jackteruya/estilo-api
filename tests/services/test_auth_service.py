import pytest
import pytest_asyncio
from datetime import timedelta
from jose import jwt
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import verify_password
from app.api.deps import get_current_user, get_current_active_superuser
from app.services.auth import (
    authenticate, create_user_token
)
from app.models.user import User
from app.models.token import Token

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
    db.rollback()
    db.query(Token).filter(Token.user_id == test_user.id).delete()
    db.commit()
    token_obj = create_user_token(
        db=db,
        user=test_user,
        expires_delta=timedelta(minutes=15)
    )
    access_token = token_obj.token
    user = get_current_user(db, access_token)
    assert user is not None
    assert user.id == test_user.id
    assert user.email == test_user.email

def test_get_current_user_invalid_token(db):
    db.rollback()
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(db, "invalid_token")
    assert exc_info.value.status_code == 401
    assert "Token inválido ou expirado" in str(exc_info.value.detail)

def test_get_current_active_user(db, test_user):
    db.rollback()
    db.query(Token).filter(Token.user_id == test_user.id).delete()
    db.commit()
    token_obj = create_user_token(
        db=db,
        user=test_user,
        expires_delta=timedelta(minutes=15)
    )
    access_token = token_obj.token
    user = get_current_user(db, access_token)
    assert user is not None
    assert user.id == test_user.id
    assert user.is_active is True

@pytest.mark.asyncio
async def test_get_current_active_superuser(db, test_superuser):
    db.rollback()
    db.query(Token).filter(Token.user_id == test_superuser.id).delete()
    db.commit()
    token_obj = create_user_token(
        db=db,
        user=test_superuser,
        expires_delta=timedelta(minutes=15)
    )
    access_token = token_obj.token
    current_user = get_current_user(db, access_token)
    user = await get_current_active_superuser(current_user=current_user)
    assert user is not None
    assert user.id == test_superuser.id
    assert user.is_superuser is True

@pytest.mark.asyncio
async def test_get_current_active_superuser_not_superuser(db, test_user):
    db.rollback()
    db.query(Token).filter(Token.user_id == test_user.id).delete()
    db.commit()
    token_obj = create_user_token(
        db=db,
        user=test_user,
        expires_delta=timedelta(minutes=15)
    )
    access_token = token_obj.token
    current_user = get_current_user(db, access_token)
    with pytest.raises(HTTPException) as exc_info:
        await get_current_active_superuser(current_user=current_user)
    assert exc_info.value.status_code == 403
    assert "O usuário não tem privilégios suficientes" in str(exc_info.value.detail) 