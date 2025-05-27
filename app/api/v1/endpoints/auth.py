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
    
    # Verifica primeiro se o usuário está inativo
    if user == "inactive":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário inativo",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Depois verifica se as credenciais são inválidas
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Cria o token com expiração de 30 minutos
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    access_token = create_access_token(
        user.id, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(
        user.id, expires_delta=refresh_token_expires
    )
    
    # Persiste o token no banco de dados
    db_token = auth_service.create_user_token(
        db=db,
        user=user,
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh", response_model=Token)
def refresh_token(
    db: Session = Depends(get_db),
    refresh_token: str = Depends(auth_service.get_refresh_token)
) -> Any:
    """
    Atualiza o access token usando o refresh token
    """
    try:
        payload = jwt.decode(
            refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
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
        
        access_token = create_access_token(
            user.id, expires_delta=access_token_expires
        )
        new_refresh_token = create_refresh_token(
            user.id, expires_delta=refresh_token_expires
        )
        
        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
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
            detail="Email já registrado",
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


@router.get("/me", response_model=User)
def read_me(current_user: User = Depends(get_current_user)):
    """
    Retorna os dados do usuário autenticado.
    """
    return current_user 