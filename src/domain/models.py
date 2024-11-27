from pydantic import BaseModel, EmailStr
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

# Modelo de usuário base
class UserBase(BaseModel):
    username: str
    email: EmailStr

# Modelo para a criação de um novo usuário
class UserCreate(UserBase):
    password: str

# Modelo de usuário com ID e data de criação
class User(UserBase):
    id: UUID = uuid4()
    created_at: datetime = datetime.now(timezone.utc)

    model_config = {
        'from_attributes': True
    }

# Hash da senha do user diretamente no banco de dados
class UserInDB(User):
    password_hash: str 