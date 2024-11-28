import pytest
from src.database.models import ChatRoom

@pytest.mark.asyncio
async def test_create_chat_room(test_client, test_db):
    # Criar usuários
    user1 = await test_client.post("/api/v1/users/", json={
        "username": "testuser1",
        "email": "test1@example.com",
        "password": "password123"
    })
    assert user1.status_code == 201
    user1_data = user1.json()

    user2 = await test_client.post("/api/v1/users/", json={
        "username": "testuser2",
        "email": "test2@example.com",
        "password": "password123"
    })
    assert user2.status_code == 201
    user2_data = user2.json()

    # Login
    login_response = await test_client.post("/api/v1/users/login", json={
        "email": "test1@example.com",
        "password": "password123"
    })
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # Criar sala
    headers = {"Authorization": f"Bearer {token}"}
    response = await test_client.post(
        "/api/v1/chat/rooms/",
        json={"user2_id": user2_data["id"]},
        headers=headers
    )

    # Verificações
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["user1_id"] == user1_data["id"]
    assert data["user2_id"] == user2_data["id"]

    # Verificar no banco
    room = test_db.query(ChatRoom).filter(ChatRoom.id == data["id"]).first()
    assert room is not None
    assert room.user1_id == user1_data["id"]
    assert room.user2_id == user2_data["id"]