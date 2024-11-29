from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

# Carrega as env vars
load_dotenv()

# Verifica se estamos em ambiente de teste pra facilitar o CI
TESTING = os.getenv("TESTING", "False").lower() == "true"

if TESTING:
    # Usa SQLite em memória para testes da mesma forma que o test_api.py
    DATABASE_URL = "sqlite:///:memory:"
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    # Configuração normal para desenvolvimento/produção
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")

    # Verifica se todas as variáveis necessárias existem
    if not all([DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME]):
        raise ValueError("Variáveis de ambiente de banco de dados não configuradas corretamente")

    # Monta a URL de conexão
    DATABASE_URL = (
        f"postgresql+psycopg2://"
        f"{DB_USER}:{quote_plus(DB_PASSWORD)}"
        f"@{DB_HOST}:{DB_PORT}"
        f"/{DB_NAME}"
    )
    
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 