from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import router
from src.database.connection import engine
from src.database.models import Base
from contextlib import asynccontextmanager

# Cria uma instância do FastAPI com configurações básicas
app = FastAPI(
    title="Chat API - YellotMob",
    description="Desafio Chat API YellotMob",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configura o middleware CORS para permitir requisições de qualquer origem
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define o ciclo de vida do aplicativo para gerenciar recursos
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Cria todas as tabelas no banco de dados
    Base.metadata.create_all(bind=engine)
    yield

# Inclui as rotas definidas no roteador
app.include_router(router)