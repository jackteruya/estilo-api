from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class TokenPayload(BaseModel):
    sub: int  # ID do usuário
    exp: datetime  # Data de expiração
    type: Optional[str] = None  # "access" ou "refresh" 