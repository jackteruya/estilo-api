from typing import Optional
from pydantic import BaseModel, EmailStr, constr


class ClientBase(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    cpf: Optional[constr(min_length=11, max_length=11)] = None
    address: Optional[str] = None


class ClientCreate(ClientBase):
    email: EmailStr
    cpf: constr(min_length=11, max_length=11)


class ClientUpdate(ClientBase):
    pass


class ClientInDBBase(ClientBase):
    id: int
    is_active: bool = True

    class Config:
        from_attributes = True


class Client(ClientInDBBase):
    pass


class ClientInDB(ClientInDBBase):
    pass 