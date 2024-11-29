from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from pytz import timezone
from src.database.connection import Base
from sqlalchemy.sql import func

class UserModel(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    
    # Adicionar relacionamentos
    sent_messages = relationship("ChatMessage", back_populates="sender")
    rooms_as_user1 = relationship("ChatRoom", foreign_keys="ChatRoom.user1_id", back_populates="user1")
    rooms_as_user2 = relationship("ChatRoom", foreign_keys="ChatRoom.user2_id", back_populates="user2")

class ChatRoom(Base):
    __tablename__ = "chat_rooms"
    
    id = Column(Integer, primary_key=True, index=True)
    user1_id = Column(Integer, ForeignKey("users.id"))
    user2_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone('America/Sao_Paulo')))
    
    # Adicionar relacionamentos
    user1 = relationship("UserModel", foreign_keys=[user1_id], back_populates="rooms_as_user1")
    user2 = relationship("UserModel", foreign_keys=[user2_id], back_populates="rooms_as_user2")
    messages = relationship("ChatMessage", back_populates="room")

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    content = Column(String)
    sender_id = Column(Integer, ForeignKey("users.id"))
    room_id = Column(Integer, ForeignKey("chat_rooms.id"))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone('America/Sao_Paulo')))
    
    # Adicionar relacionamentos
    sender = relationship("UserModel", back_populates="sent_messages")
    room = relationship("ChatRoom", back_populates="messages")