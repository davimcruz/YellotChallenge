from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, List
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    
    model_config = ConfigDict(from_attributes=True)

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    
    model_config = ConfigDict(from_attributes=True)

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str
    
    model_config = ConfigDict(from_attributes=True)

class Message(BaseModel):
    content: str
    sender_username: str
    created_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)

    # Formata a data de criação para o padrão brasileiro
    @property
    def formatted_date(self):
        return self.created_at.strftime("%d/%m/%Y %H:%M:%S") if self.created_at else None