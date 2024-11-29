from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.database.connection import get_db
from src.domain.schemas import UserCreate, UserResponse, UserLogin, Token
from src.services.user_service import UserService

router = APIRouter()
# Cria um usuário
@router.post(
    "/users/", 
    response_model=UserResponse, 
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Usuário criado com sucesso"},
        400: {"description": "Email já cadastrado"}
    }
)
async def create_user(
    user_data: UserCreate, 
    db: Session = Depends(get_db)
):
    try:
        return UserService.create_user(db=db, user_data=user_data)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/users/login", response_model=Token)
async def login(login_data: UserLogin, db: Session = Depends(get_db)):
    return UserService.authenticate_user(db=db, login_data=login_data)
