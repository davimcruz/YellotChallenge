import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from src.main import app
from src.services.auth_service import SECRET_KEY, ALGORITHM
import jwt
from fastapi import WebSocketDisconnect

@pytest.mark.asyncio
async def test_websocket_connection(test_client):
    # Etapa 1: Criar os dois usuarios da sala e fazer login
    print("Etapa 1: Criando usuários e realizando login...")
    user1 = await test_client.post("/api/v1/users/", json={
        "username": "yellot1",
        "email": "yellot1@example.com",
        "password": "senha123"
    })
    assert user1.status_code == 201
    user1_data = user1.json()

    user2 = await test_client.post("/api/v1/users/", json={
        "username": "yellot2",
        "email": "yellot2@example.com",
        "password": "senha123"
    })
    assert user2.status_code == 201
    user2_data = user2.json()

    login1 = await test_client.post("/api/v1/users/login", json={
        "email": "yellot1@example.com",
        "password": "senha123"
    })
    assert login1.status_code == 200
    token1 = login1.json()["access_token"]

    login2 = await test_client.post("/api/v1/users/login", json={
        "email": "yellot2@example.com",
        "password": "senha123"
    })
    assert login2.status_code == 200
    token2 = login2.json()["access_token"]

    # Etapa 2: Criar sala ou verificar se já existe
    print("Etapa 2: Criando sala de chat...")
    headers = {"Authorization": f"Bearer {token1}"}
    response = await test_client.post(
        "/api/v1/chat/rooms/",
        json={"user2_id": user2_data["id"]},
        headers=headers
    )
    assert response.status_code == 201, f"Falha ao criar sala: {response.status_code}"
    room_id = response.json()["id"]
    print(f"Sala criada com ID: {room_id}")

    # Etapa 3: Conectar ao WebSocket
    print("Etapa 3: Conectando ao WebSocket...")
    with TestClient(app) as client:
        try:
            with client.websocket_connect(
                f"/api/v1/chat/ws/{room_id}?token={token1}"
            ) as websocket1, client.websocket_connect(
                f"/api/v1/chat/ws/{room_id}?token={token2}"
            ) as websocket2:
                print("Conexão WebSocket estabelecida.")

                # Etapa 4: Teste de envio e recebimento de mensagens
                print("Etapa 4: Testando envio e recebimento de mensagens...")
                message1 = {"content": "Eai usuário 1!"}
                websocket1.send_json(message1)
                received1 = websocket2.receive_json()
                assert "message" in received1, "Mensagem não recebida pelo usuário 2"
                assert received1["message"] == message1["content"], "Conteúdo da mensagem incorreto"
                assert received1["user_id"] == user1_data["id"], "ID do usuário está incorreto"
                print("Mensagem 1 enviada e recebida com sucesso")

                message2 = {"content": "Olá do usuário 2!"}
                websocket2.send_json(message2)
                received2 = websocket1.receive_json()
                assert "message" in received2, "Mensagem não recebida pelo usuário 1"
                assert received2["message"] == message2["content"], "Conteúdo da mensagem incorreto"
                assert received2["user_id"] == user2_data["id"], "ID do usuário incorreto"
                print("Mensagem 2 enviada e recebida com sucesso.")
        except WebSocketDisconnect as e:
            print(f"Erro ao conectar ao WebSocket: {e}")

@pytest.mark.asyncio
async def test_websocket_unauthorized(test_client):
    with TestClient(app) as client:
        with pytest.raises(Exception):
            with client.websocket_connect("/api/v1/chat/ws/1") as websocket:
                pass

@pytest.mark.asyncio
async def test_websocket_invalid_room(test_client, login_users):
    token, _, _, _ = login_users
    with TestClient(app) as client:
        with pytest.raises(Exception):
            with client.websocket_connect(
                f"/api/v1/chat/ws/999?token={token}"
            ) as websocket:
                pass

@pytest.fixture
async def login_users(test_client):
    # Criar usuários simulados
    user1 = await test_client.post("/api/v1/users/", json={
        "username": "yellot1",
        "email": "yellot1@example.com",
        "password": "senha123"
    })
    user2 = await test_client.post("/api/v1/users/", json={
        "username": "yellot2",
        "email": "yellot2@example.com",
        "password": "senha123"
    })

    # Login dos usuários
    login1 = await test_client.post("/api/v1/users/login", json={
        "email": "yellot1@example.com",
        "password": "senha123"
    })
    login2 = await test_client.post("/api/v1/users/login", json={
        "email": "yellot2@example.com",
        "password": "senha123"
    })

    return login1.json()["access_token"], login2.json()["access_token"], user1.json(), user2.json()