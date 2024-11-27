from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from src.database.connection import Base
import datetime

# Model base dos usuários
class UserModel(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String, unique=True, index=True)  # Email único 
    username = Column(String, index=True)
    password_hash = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow) 

    # Relacionamentos para mensagens enviadas/recebidas
    sent_messages = relationship("ChatMessage", foreign_keys="ChatMessage.sender_id", back_populates="sender")
    received_messages = relationship("ChatMessage", foreign_keys="ChatMessage.receiver_id", back_populates="receiver")

# Mensagens do chat
class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    content = Column(String)
    sender_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    receiver_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    read_at = Column(DateTime, nullable=True)  # Para marcar quando a mensagem foi lida
    
    # Relacionamentos
    sender = relationship("UserModel", foreign_keys=[sender_id], back_populates="sent_messages")
    receiver = relationship("UserModel", foreign_keys=[receiver_id], back_populates="received_messages")