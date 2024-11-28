from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.auth_routes import router as auth_router
from src.api.chat_routes import router as chat_router
from src.database.connection import engine
from src.database.models import Base

app = FastAPI(
    title="Chat API",
    description="API de chat com autenticação JWT",
    version="1.0.0"
)

# Criar tabelas no startup
@app.on_event("startup")
async def startup():
    # Criar todas as tabelas definidas
    Base.metadata.create_all(bind=engine)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rotas
app.include_router(auth_router, prefix="/api/v1", tags=["Auth"])
app.include_router(chat_router, prefix="/api/v1/chat", tags=["Chat"])