from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from src.database.models import UserModel
from src.domain.schemas import UserCreate, UserResponse, UserLogin, Token
from src.services.auth_service import create_access_token
import bcrypt
from datetime import datetime, UTC


class UserService:
    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> UserResponse:
        try:
            # Verificar se email já existe
            existing_user = db.query(UserModel).filter(
                UserModel.email == user_data.email
            ).first()
            
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email já cadastrado"
                )
            
            # Hash da senha
            hashed_password = bcrypt.hashpw(
                user_data.password.encode('utf-8'), 
                bcrypt.gensalt()
            )
            
            # Criar usuário
            user = UserModel(
                username=user_data.username,
                email=user_data.email,
                password=hashed_password.decode('utf-8')
            )
            
            db.add(user)
            db.commit()
            db.refresh(user)
            return UserResponse.model_validate(user)
            
        except HTTPException:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao criar usuário: {str(e)}"
            )
    
    # Autentica de fato o usuário e retorna um token JWT contendo seu id intrisicamente
    @staticmethod
    def authenticate_user(db: Session, login_data: UserLogin) -> Token:
        user = db.query(UserModel).filter(UserModel.email == login_data.email).first()
        if not user:
            raise HTTPException(status_code=401, detail="Usuário não encontrado")
        
        if not bcrypt.checkpw(login_data.password.encode('utf-8'), user.password.encode('utf-8')):
            raise HTTPException(status_code=401, detail="Senha incorreta")
        
        access_token = create_access_token({"sub": str(user.id)})
        return Token(access_token=access_token, token_type="bearer")