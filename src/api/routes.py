from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from src.domain.models import UserCreate, User
from src.services.user_service import UserService
from src.database.connection import get_db
from src.services.auth_service import get_current_user

router = APIRouter(prefix="/api/v1")

# Rota para criar um novo usuário
@router.post(
    "/users/",
    response_model=User,
    tags=["Users"],
    summary="Cria um novo usuário",
    description="Cria um novo usuário no sistema com os dados fornecidos.",
    responses={
        200: {"description": "Usuário criado com sucesso."},
        400: {"description": "Email já registrado."},
        500: {"description": "Erro ao criar usuário."}
    }
)
async def create_user(
    user: UserCreate = Body(
        ...,
        examples={
            "example1": {
                "summary": "Exemplo de criação de usuário",
                "description": "Um exemplo de como criar um novo usuário.",
                "value": {
                    "username": "newuser",
                    "email": "newuser@example.com",
                    "password": "password123"
                }
            }
        }
    ),
    db: Session = Depends(get_db)
) -> User:
    """
    Cria um novo usuário.

    - **username**: Nome de usuário único
    - **email**: Endereço de email único
    - **password**: Senha do usuário
    """
    return UserService.create_user(db, user)

# Rota para listar todos os usuários (protegida)
@router.get(
    "/users/",
    response_model=List[User],
    tags=["Users"],
    summary="Lista todos os usuários",
    description="Retorna uma lista de todos os usuários cadastrados no sistema.",
    responses={
        200: {"description": "Lista de usuários retornada com sucesso."},
        401: {"description": "Token inválido ou não fornecido."}
    }
)
async def list_users(
    db: Session = Depends(get_db)
) -> List[User]:
    """
    Lista todos os usuários cadastrados.

    Retorna uma lista de objetos de usuário.
    """
    return UserService.get_users(db)

# Rota para login
@router.post(
    "/login/",
    tags=["Auth"],
    summary="Realiza login",
    description="Autentica o usuário e retorna um token de acesso.",
    responses={
        200: {"description": "Login realizado com sucesso."},
        401: {"description": "Credenciais inválidas."}
    }
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Realiza login no sistema.

    - **username**: Email do usuário
    - **password**: Senha do usuário
    """
    return UserService.login_user(db, form_data.username, form_data.password) 