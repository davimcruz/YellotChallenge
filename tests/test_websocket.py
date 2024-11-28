import pytest
import logging
from fastapi.testclient import TestClient
from src.main import app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.fixture
async def create_users(test_client):
    # Criar usuários simulados
    user1 = await test_client.post("/api/v1/users/", json={
        "username": "user1",
        "email": "user1@test.com",
        "password": "password123"
    })
    user2 = await test_client.post("/api/v1/users/", json={
        "username": "user2",
        "email": "user2@test.com",
        "password": "password123"
    })
    return user1.json(), user2.json()

@pytest.fixture
async def login_users(test_client, create_users):
    user1_data, user2_data = create_users
    login1 = await test_client.post("/api/v1/users/login", json={
        "email": "user1@test.com",
        "password": "password123"
    })
    login2 = await test_client.post("/api/v1/users/login", json={
        "email": "user2@test.com",
        "password": "password123"
    })
    return login1.json()["access_token"], login2.json()["access_token"], user1_data, user2_data

@pytest.fixture
async def create_room(test_client, login_users):
    token1, _, user1_data, user2_data = login_users
    headers = {"Authorization": f"Bearer {token1}"}
    room = await test_client.post(
        "/api/v1/chat/rooms/",
        json={"user2_id": user2_data["id"]},
        headers=headers
    )
    return room.json()["id"]

@pytest.mark.asyncio
async def test_websocket_connection(test_client, create_room, login_users):
    token1, token2, user1_data, user2_data = login_users
    room_id = create_room

    with TestClient(app) as client:
        with client.websocket_connect(
            f"/api/v1/chat/ws/{room_id}?token={token1}"
        ) as websocket1, client.websocket_connect(
            f"/api/v1/chat/ws/{room_id}?token={token2}"
        ) as websocket2:
            
            # Teste: Usuário 1 envia, Usuário 2 recebe
            message1 = {"content": "Olá do usuário 1!"}
            websocket1.send_json(message1)
            received1 = websocket2.receive_json()
            assert "message" in received1
            assert received1["message"] == message1["content"]
            assert received1["user_id"] == user1_data["id"]
            
            # Teste: Usuário 2 envia, Usuário 1 recebe
            message2 = {"content": "Olá do usuário 2!"}
            websocket2.send_json(message2)
            received2 = websocket1.receive_json()
            assert "message" in received2
            assert received2["message"] == message2["content"]
            assert received2["user_id"] == user2_data["id"]

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