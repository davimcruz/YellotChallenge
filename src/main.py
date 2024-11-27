from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import router
from src.database.connection import engine, Base
import logging

logger = logging.getLogger(__name__)

# Cria as tabelas no primeiro start da API
logger.info("Iniciando criação das tabelas no banco de dados...")
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Tabelas criadas com sucesso!")
except Exception as e:
    logger.error(f"Erro ao criar tabelas: {str(e)}")
    raise

# Config básica da API
app = FastAPI(
    title="Chat API - YellotMob",
    description="Chat API com websocket e JWT",
    version="1.0.0",
)

# CORS - permitindo todas as origens por enquanto
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclui as rotas com o prefixo correto e com descrição pra tratamento de erros
app.include_router(
    router,
    prefix="/api/v1",
    tags=["users"],
    responses={
        400: {"description": "Requisição inválida"},
        401: {"description": "Não autorizado"},
        404: {"description": "Recurso não encontrado"},
        500: {"description": "Erro interno do servidor"}
    }
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)