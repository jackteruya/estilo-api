from typing import Optional
from datetime import datetime, timedelta

from jose import jwt
from sqlalchemy.orm import Session

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.security import get_password_hash, verify_password, create_access_token
from app.models.user import User
from app.schemas.user import UserCreate
from app.models.token import Token
from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"/api/v1/auth/login")


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def authenticate(db: Session, email: str, password: str) -> User | str | bool:
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return False
    if not user.is_active:
        return "inactive"
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_user(db: Session, *, obj_in: UserCreate) -> User:
    db_obj = User(
        email=obj_in.email,
        hashed_password=get_password_hash(obj_in.password),
        full_name=obj_in.full_name,
        is_superuser=obj_in.is_superuser,
        is_active=obj_in.is_active if obj_in.is_active is not None else True
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


async def get_refresh_token(token: str = Depends(oauth2_scheme)) -> str:
    """
    Dependência para obter o refresh token do header Authorization
    """
    return token


def create_user_token(
    db: Session,
    *,
    user: User,
    expires_delta: Optional[timedelta] = None
) -> Token:
    """
    Cria um novo token para o usuário e o persiste no banco de dados.
    """
    # Desativa tokens anteriores do usuário
    db.query(Token).filter(
        Token.user_id == user.id,
        Token.is_active == True
    ).update({"is_active": False})
    
    # Cria o token
    access_token = create_access_token(
        subject=user.id,
        expires_delta=expires_delta
    )
    
    # Define a data de expiração
    if expires_delta:
        expires_at = datetime.utcnow() + expires_delta
    else:
        expires_at = datetime.utcnow() + timedelta(minutes=15)
    
    # Cria o registro do token
    db_token = Token(
        token=access_token,
        user_id=user.id,
        expires_at=expires_at,
        is_active=True
    )
    
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    
    return db_token


def get_active_token(db: Session, token: str) -> Optional[Token]:
    """
    Busca um token ativo no banco de dados.
    """
    return db.query(Token).filter(
        Token.token == token,
        Token.is_active == True,
        Token.expires_at > datetime.utcnow()
    ).first()


def deactivate_token(db: Session, token: str) -> None:
    """
    Desativa um token específico.
    """
    db.query(Token).filter(Token.token == token).update({"is_active": False})
    db.commit()


def deactivate_user_tokens(db: Session, user_id: int) -> None:
    """
    Desativa todos os tokens de um usuário.
    """
    db.query(Token).filter(
        Token.user_id == user_id,
        Token.is_active == True
    ).update({"is_active": False})
    db.commit()


def get_current_user(db: Session, token: str) -> User:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido ou expirado"
            )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado"
        )
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise HTTPException(
            status_code=400,
            detail="Usuário inativo"
        )
    return current_user


def get_current_active_superuser(db: Session, token: str) -> User:
    user = get_current_active_user(db, token)
    if not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão negada"
        )
    return user


def validate_token(token: str) -> bool:
    """
    Valida um token JWT.
    Retorna True se o token for válido, False caso contrário.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return True
    except jwt.JWTError:
        return False


def logout(db: Session, token: str) -> bool:
    """
    Realiza o logout do usuário invalidando o token.
    Retorna True se o logout foi bem sucedido, False caso contrário.
    """
    try:
        # Verifica se o token é válido
        if not validate_token(token):
            return False
            
        # Desativa o token no banco de dados
        deactivate_token(db, token)
        return True
    except Exception:
        return False 