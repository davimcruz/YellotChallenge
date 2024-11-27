from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.database.connection import get_db
from src.domain.models import UserCreate, User
from src.services.user_service import UserService
from fastapi.security import OAuth2PasswordRequestForm

# Cria o router 
router = APIRouter()

# Define as rotas a serem utilizadas juntamente com as respostas e descrições para o swagger
@router.post("/users/", 
    response_model=User,
    summary="Criar novo usuário",
    description="Cria um novo usuário com username, email e senha",
    responses={
        200: {
            "description": "Usuário criado com sucesso",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "username": "exemplo",
                        "email": "exemplo@email.com",
                        "created_at": "2024-01-01T00:00:00"
                    }
                }
            }
        }
    }
)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    return UserService.create_user(db, user)

@router.get("/users/",
    response_model=list[User],
    summary="Listar usuários",
    description="Lista todos os usuários cadastrados no sistema",
    responses={
        200: {
            "description": "Lista de usuários retornada com sucesso",
            "content": {
                "application/json": {
                    "example": [{
                        "id": 1,
                        "username": "exemplo",
                        "email": "exemplo@email.com",
                        "created_at": "2024-01-01T00:00:00"
                    }]
                }
            }
        }
    }
)
async def list_users(db: Session = Depends(get_db)):
    return UserService.get_users(db)

@router.post("/login/",
    summary="Autenticar usuário",
    description="Autentica um usuário e retorna um token JWT",
    responses={
        200: {
            "description": "Login bem-sucedido",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1...",
                        "token_type": "bearer"
                    }
                }
            }
        }
    }
)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    return UserService.login_user(db, form_data.username, form_data.password) 