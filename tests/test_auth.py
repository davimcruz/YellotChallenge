import pytest
from src.database.models import UserModel
import bcrypt
import jwt
from src.services.auth_service import SECRET_KEY, ALGORITHM

# Testa a criação de usuário
@pytest.mark.asyncio
async def test_create_user(test_client):
    response = await test_client.post("/api/v1/users/", json={
        "username": "yellot",
        "email": "yellot@example.com",
        "password": "senha123"
    })
    assert response.status_code == 201
    assert "id" in response.json()
    assert response.json()["email"] == "yellot@example.com"

@pytest.mark.asyncio
async def test_create_duplicate_user(test_client):
    # Primeiro usuário
    await test_client.post("/api/v1/users/", json={
        "username": "yellot1",
        "email": "yellot1@example.com",
        "password": "senha123"
    })
    
    # Tentar criar usuário com mesmo email
    response = await test_client.post("/api/v1/users/", json={
        "username": "yellot2",
        "email": "yellot1@example.com",
        "password": "senha123"
    })
    assert response.status_code == 400
    assert "Email já cadastrado" in response.json()["detail"]

@pytest.mark.asyncio
async def test_login(test_client, test_db):
    # Criar usuário
    hashed_password = bcrypt.hashpw("senha123".encode('utf-8'), bcrypt.gensalt())
    user = UserModel(
        username="testuser", 
        email="yellot@example.com", 
        password=hashed_password.decode('utf-8')
    )
    test_db.add(user)
    test_db.commit()

    # Login
    response = await test_client.post("/api/v1/users/login", json={
        "email": "yellot@example.com",
        "password": "senha123"
    })
    
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_jwt_contains_user_id(test_client):
    # Criar usuário com email único
    create_response = await test_client.post("/api/v1/users/", json={
        "username": "testuser_jwt",
        "email": "yellot@example.com",  # Email único para este teste
        "password": "senha123"
    })
    assert create_response.status_code == 201
    user_id = create_response.json()["id"]
    
    # Login com o novo usuário
    login_response = await test_client.post("/api/v1/users/login", json={
        "email": "yellot@example.com",  # Usar o mesmo email
        "password": "senha123"
    })
    assert login_response.status_code == 200
    
    # Verificar token
    token = login_response.json()["access_token"]
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    
    # Verificações
    assert "sub" in payload
    assert str(user_id) == payload["sub"]
    assert "exp" in payload
