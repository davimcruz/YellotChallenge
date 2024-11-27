import sys
import os
from datetime import datetime, timezone
from sqlalchemy.orm import declarative_base
import uuid

# Adiciona o diretório 'src' ao caminho do sistema para importar módulos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import pytest
from httpx import AsyncClient, ASGITransport
from src.main import app

# Cria uma base declarativa para o SQLAlchemy
Base = declarative_base()

@pytest.mark.asyncio
async def test_create_user():
    # Gera um UUID único para garantir que o nome de usuário e email sejam únicos
    unique_id = str(uuid.uuid4())
    username = f"user_{unique_id}"
    email = f"user_{unique_id}@example.com"

    # Cria um cliente HTTP assíncrono para testar a API
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/v1/users/", json={
            "username": username,
            "email": email,
            "password": "password123"
        })
    # Verifica se a resposta HTTP é 200 OK
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_login():
    # Cria um cliente HTTP assíncrono para testar a API
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Cria um usuário para garantir que ele exista antes de tentar o login
        await ac.post("/api/v1/users/", json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123"
        })
        
        # Tenta fazer login com o usuário criado
        response = await ac.post("/api/v1/login/", data={
            "username": "test@example.com",
            "password": "password123"
        })
    # Verifica se a resposta HTTP é 200 OK
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_list_users():
    # Cria um cliente HTTP assíncrono para testar a API
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Faz login para obter um token de acesso
        login_response = await ac.post("/api/v1/login/", data={
            "username": "test@example.com",
            "password": "password123"
        })
        token = login_response.json().get("access_token")
        # Verifica se o token de acesso foi obtido
        assert token is not None, "Token de acesso não encontrado"

        # Usa o token de acesso para listar os usuários
        response = await ac.get("/api/v1/users/", headers={
            "Authorization": f"Bearer {token}"
        })
    # Verifica se a resposta HTTP é 200 OK e se a resposta é uma lista
    assert response.status_code == 200
    assert isinstance(response.json(), list) 