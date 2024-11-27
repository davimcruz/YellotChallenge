from sqlalchemy.orm import Session
from passlib.context import CryptContext
from fastapi import HTTPException
from src.database.models import UserModel
from src.domain.models import UserCreate, User
from typing import List
from src.services.auth_service import create_access_token
import logging
from sqlalchemy.exc import IntegrityError

# Configura o contexto de criptografia para senhas usando o bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
logger = logging.getLogger(__name__)

# Serviço para gerenciar operações relacionadas a usuários
class UserService:
    @staticmethod
    def get_password_hash(password: str) -> str:
        # Gera o hash da senha usando bcrypt
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        # Verifica se a senha fornecida corresponde ao hash armazenado
        return pwd_context.verify(plain_password, hashed_password)

    # Método para criar um novo usuário
    @staticmethod
    def create_user(db: Session, user: UserCreate) -> User:
        logger.info(f"Tentando criar usuário: {user.email}")
        # Verifica se o email já está registrado
        existing_user = db.query(UserModel).filter(UserModel.email == user.email).first()
        if existing_user:
            logger.warning(f"Email já registrado: {user.email}")
            raise HTTPException(status_code=400, detail="Email já registrado")

        try:
            # Cria um novo usuário no banco de dados
            db_user = UserModel(
                username=user.username,
                email=user.email,
                password_hash=UserService.get_password_hash(user.password)
            )
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            logger.info(f"Usuário criado com sucesso: {user.email}")
            return User.model_validate(db_user)
        except IntegrityError as e:
            db.rollback()
            # Trata erros de unicidade
            if "unique constraint" in str(e.orig):
                raise HTTPException(status_code=400, detail="Nome de usuário ou email já registrado")
            raise HTTPException(status_code=500, detail="Erro ao criar usuário")

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str):
        # Autentica o usuário verificando email e senha
        user = db.query(UserModel).filter(UserModel.email == email).first()
        if not user or not UserService.verify_password(password, user.password_hash):
            raise HTTPException(status_code=401, detail="Credenciais inválidas")
        return user

    @staticmethod
    def login_user(db: Session, email: str, password: str):
        # Realiza o login do usuário e gera um token de acesso
        user = UserService.authenticate_user(db, email, password)
        access_token = create_access_token(data={"sub": str(user.id), "name": user.username})
        return {"access_token": access_token, "token_type": "bearer"}

    # Método para obter todos os usuários
    @staticmethod
    def get_users(db: Session) -> List[User]:
        # Retorna uma lista de todos os usuários
        users = db.query(UserModel).all()
        return [User.model_validate(user) for user in users] 