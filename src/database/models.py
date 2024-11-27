from sqlalchemy import Column, Integer, String, DateTime
from src.database.connection import Base
import datetime

# Model base dos usuários
class UserModel(Base):
    __tablename__ = "users"

    # Índices nas colunas mais acessadas
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String, unique=True, index=True)  # Email único 
    username = Column(String, index=True)
    password_hash = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow) 