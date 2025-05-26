from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token
from app.db.base import get_db
from app.schemas.token import Token, TokenPayload
from app.schemas.user import UserCreate, User
from app.services import auth as auth_service
from app.api.deps import get_current_user

router = APIRouter()


@router.post("/login", response_model=Token)
def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    Obtém um token de acesso para autenticação.
    """
    user = auth_service.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário inativo"
        )
    
    # Cria o token com expiração de 30 minutos
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    db_token = auth_service.create_user_token(
        db=db,
        user=user,
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": db_token.token,
        "token_type": "bearer"
    }


@router.post("/refresh-token", response_model=Token)
def refresh_token(
    db: Session = Depends(get_db),
    refresh_token: str = Depends(auth_service.get_refresh_token)
) -> Any:
    """
    Atualiza o access token usando o refresh token
    """
    try:
        payload = jwt.decode(
            refresh_token, settings.SECRET_KEY, algorithms=["HS256"]
        )
        token_data = TokenPayload(**payload)
        
        if token_data.type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido",
            )
            
        user = auth_service.get_user(db, user_id=token_data.sub)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário não encontrado",
            )
            
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
        return {
            "access_token": create_access_token(
                user.id, expires_delta=access_token_expires
            ),
            "refresh_token": create_refresh_token(
                user.id, expires_delta=refresh_token_expires
            ),
            "token_type": "bearer",
        }
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
        )


@router.post("/register", response_model=User)
def register(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
) -> Any:
    """
    Criar novo usuário.
    """
    user = auth_service.get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="O email já está registrado.",
        )
    user = auth_service.create_user(db, obj_in=user_in)
    return user


@router.post("/logout")
def logout(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Desativa o token atual do usuário.
    """
    auth_service.deactivate_user_tokens(db, current_user.id)
    return {"message": "Logout realizado com sucesso"} 