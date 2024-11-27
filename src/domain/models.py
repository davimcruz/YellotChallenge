from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# Modelo de usuário base
class UserBase(BaseModel):
    username: str
    email: EmailStr

# Modelo para a criação de um novo usuário
class UserCreate(UserBase):
    password: str

# Modelo de usuário com ID e data de criação
class User(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Hash da senha do user diretamente no banco de dados
class UserInDB(User):
    password_hash: str 

class Token(BaseModel):
    access_token: str
    token_type: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }
    }