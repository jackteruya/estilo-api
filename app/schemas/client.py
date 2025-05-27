from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, constr, validator


class ClientBase(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    cpf: Optional[str] = None
    address: Optional[str] = None

    @validator('cpf')
    def validate_cpf(cls, v):
        if v is None:
            return v
        # Remove caracteres não numéricos
        cpf = ''.join(filter(str.isdigit, v))
        if len(cpf) != 11:
            raise ValueError('CPF deve conter 11 dígitos')
        return cpf


class ClientCreate(ClientBase):
    email: EmailStr
    cpf: str

    @validator('cpf')
    def validate_cpf(cls, v):
        if v is None:
            raise ValueError('CPF é obrigatório')
        # Remove caracteres não numéricos
        cpf = ''.join(filter(str.isdigit, v))
        if len(cpf) != 11:
            raise ValueError('CPF deve conter 11 dígitos')
        return cpf


class ClientUpdate(ClientBase):
    pass


class ClientInDBBase(ClientBase):
    id: int
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Client(ClientInDBBase):
    pass


class ClientInDB(ClientInDBBase):
    pass 