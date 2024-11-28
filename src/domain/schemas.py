from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    username: str
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    created_at: Optional[datetime] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }
    )

class ChatRoomBase(BaseModel):
    user2_id: int
    
    model_config = ConfigDict(from_attributes=True)

class ChatRoomCreate(ChatRoomBase):
    pass

class ChatRoomResponse(BaseModel):
    id: int
    user1_id: int
    user2_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class ChatMessageBase(BaseModel):
    content: str
    
    model_config = ConfigDict(from_attributes=True)

class ChatMessageCreate(ChatMessageBase):
    pass

class ChatMessageResponse(BaseModel):
    id: int
    content: str
    sender_id: int
    room_id: int
    created_at: datetime
    sender_username: str
    
    model_config = ConfigDict(from_attributes=True)