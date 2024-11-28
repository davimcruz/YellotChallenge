import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.main import app
from src.database.connection import get_db, Base

# Configuração do banco de dados em memória para testes (na primeira versão era executado diretamente em um banco de dados para desenvolvimento, entretanto, atrapalharia no CI)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="function")
async def test_app():
    # Criar engine do SQLite em memória
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Criar todas as tabelas
    Base.metadata.create_all(bind=engine)

    async def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    
    yield app  # inicia o teste
    
    # Limpeza das tabelas
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_create_user(test_app):
    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as ac:
        response = await ac.post("/api/v1/users/", json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123"
        })
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_login(test_app):
    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as ac:
        # Criar usuário primeiro
        await ac.post("/api/v1/users/", json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123"
        })
        
        # Tentar login
        response = await ac.post("/api/v1/login/", data={
            "username": "test@example.com",
            "password": "password123"
        })
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_list_users(test_app):
    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as ac:
        # Criar e logar usuário
        await ac.post("/api/v1/users/", json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123"
        })
        
        login_response = await ac.post("/api/v1/login/", data={
            "username": "test@example.com",
            "password": "password123"
        })
        token = login_response.json().get("access_token")
        assert token is not None

        response = await ac.get("/api/v1/users/", headers={
            "Authorization": f"Bearer {token}"
        })
    assert response.status_code == 200
    assert isinstance(response.json(), list) 