from sqlalchemy.orm import Session
from passlib.context import CryptContext
from fastapi import HTTPException
from src.database.models import UserModel
from src.domain.models import UserCreate, User
from typing import List
from src.services.auth_service import create_access_token
import logging
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

# logging básico pra obter alguns detalhes em debugging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:
    @staticmethod
    def get_password_hash(password: str) -> str:
        try:
            hashed = pwd_context.hash(password)
            logger.debug(f"Senha hash gerada com sucesso")
            return hashed
        except Exception as e:
            logger.error(f"Erro ao gerar hash da senha: {str(e)}")
            raise

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        try:
            result = pwd_context.verify(plain_password, hashed_password)
            logger.debug(f"Verificação de senha realizada: {'sucesso' if result else 'falha'}")
            return result
        except Exception as e:
            logger.error(f"Erro ao verificar senha: {str(e)}")
            raise

    @staticmethod
    def create_user(db: Session, user: UserCreate) -> User:
        logger.info(f"Iniciando criação de usuário com email: {user.email}")
        
        try:
            # Verifica email existente
            logger.debug(f"Verificando se email já existe: {user.email}")
            existing_user = db.query(UserModel).filter(UserModel.email == user.email).first()
            
            if existing_user:
                logger.warning(f"Tentativa de criar usuário com email já existente: {user.email}")
                raise HTTPException(status_code=400, detail="Email já registrado")

            # Cria hash da senha
            logger.debug("Gerando hash da senha")
            password_hash = UserService.get_password_hash(user.password)

            # Cria novo usuário
            logger.debug(f"Criando novo usuário com username: {user.username}")
            db_user = UserModel(
                username=user.username,
                email=user.email,
                password_hash=password_hash
            )

            # Adiciona e commita no banco
            logger.debug("Adicionando usuário ao banco de dados")
            db.add(db_user)
            db.commit()
            logger.debug("Commit realizado com sucesso")
            
            db.refresh(db_user)
            logger.info(f"Usuário criado com sucesso: ID={db_user.id}, Email={user.email}")
            
            return User.model_validate(db_user)

        except IntegrityError as e:
            logger.error(f"Erro de integridade ao criar usuário: {str(e)}")
            db.rollback()
            raise HTTPException(status_code=500, detail="Erro de integridade ao criar usuário")
        except SQLAlchemyError as e:
            logger.error(f"Erro do SQLAlchemy ao criar usuário: {str(e)}")
            db.rollback()
            raise HTTPException(status_code=500, detail="Erro no banco de dados")
        except Exception as e:
            logger.error(f"Erro inesperado ao criar usuário: {str(e)}")
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Erro ao criar usuário: {str(e)}")

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str):
        logger.info(f"Tentativa de autenticação para email: {email}")
        try:
            user = db.query(UserModel).filter(UserModel.email == email).first()
            if not user:
                logger.warning(f"Usuário não encontrado para email: {email}")
                raise HTTPException(status_code=401, detail="Credenciais inválidas")
            
            if not UserService.verify_password(password, user.password_hash):
                logger.warning(f"Senha incorreta para email: {email}")
                raise HTTPException(status_code=401, detail="Credenciais inválidas")
            
            logger.info(f"Autenticação bem-sucedida para email: {email}")
            return user
        except Exception as e:
            logger.error(f"Erro durante autenticação: {str(e)}")
            raise

    @staticmethod
    def login_user(db: Session, email: str, password: str):
        logger.info(f"Tentativa de login para email: {email}")
        try:
            user = UserService.authenticate_user(db, email, password)
            access_token = create_access_token(data={"sub": str(user.id), "name": user.username})
            logger.info(f"Login bem-sucedido para email: {email}")
            return {"access_token": access_token, "token_type": "bearer"}
        except Exception as e:
            logger.error(f"Erro durante login: {str(e)}")
            raise

    @staticmethod
    def get_users(db: Session) -> List[User]:
        logger.info("Buscando lista de usuários")
        try:
            users = db.query(UserModel).all()
            logger.info(f"Total de usuários encontrados: {len(users)}")
            return [User.model_validate(user) for user in users]
        except Exception as e:
            logger.error(f"Erro ao buscar usuários: {str(e)}")
            raise 