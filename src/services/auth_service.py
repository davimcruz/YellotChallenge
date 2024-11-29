from fastapi import HTTPException, status
from jose import JWTError, jwt
from datetime import datetime, timedelta
import bcrypt
from sqlalchemy.orm import Session
from src.database.models import UserModel
import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do .env, tipo, pra não deixar segredos no código
load_dotenv()

# Pega a SECRET_KEY do .env. Sem ela, nada de tokens seguros!
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY não encontrada no arquivo .env")

ALGORITHM = "HS256"  # Algoritmo padrão pra JWT, bem seguro e comum
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Tokens expiram em 30 minutos, pra segurança extra

def create_access_token(data: dict):
    # Copia os dados e adiciona um tempo de expiração
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    # Codifica tudo em um JWT usando nossa SECRET_KEY
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str, db: Session = None) -> dict:
    try:
        # Decodifica o token pra pegar o ID do usuário
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            # Se não tiver ID, o token é inválido
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )
        return {"id": user_id}
    except JWTError:
        # Qualquer erro na decodificação significa token inválido
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )
