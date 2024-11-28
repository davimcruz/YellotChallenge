from fastapi import APIRouter, Depends, WebSocket, HTTPException, status, Header
from sqlalchemy.orm import Session
from src.database.connection import get_db
from src.services.auth_service import get_current_user
from src.services.chat_service import ChatService
from src.services.websocket_manager import manager
from pydantic import BaseModel
import logging
import json

router = APIRouter()
logger = logging.getLogger(__name__)

# Adicione este schema
class RoomCreate(BaseModel):
    user2_id: int

@router.post("/rooms/", status_code=201)
async def create_chat_room(
    room: RoomCreate,
    authorization: str = Header(...),
    db: Session = Depends(get_db)
):
    try:
        token = authorization.split(" ")[1]
        current_user = await get_current_user(token)
        user1_id = int(current_user["id"])
        
        room = ChatService.create_room(db, user1_id, room.user2_id)
        
        return {
            "id": room.id,
            "user1_id": room.user1_id,
            "user2_id": room.user2_id
        }
    except Exception as e:
        logger.error(f"Erro ao criar sala: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.websocket("/ws/{room_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    room_id: int,
    token: str = None
):
    if not token:
        await websocket.close(code=1008)
        return

    try:
        current_user = await get_current_user(token)
        user_id = int(current_user["id"])
        
        db = next(get_db())
        try:
            room = ChatService.get_room(db, room_id, user_id)
            await manager.connect(websocket, room_id, user_id)
            
            try:
                while True:
                    data = await websocket.receive_text()
                    message = json.loads(data)
                    
                    chat_message = ChatService.create_message(
                        db=db,
                        room_id=room_id,
                        user_id=user_id,
                        content=message.get("content", "")
                    )
                    
                    await manager.broadcast(
                        {
                            "id": chat_message.id,
                            "content": chat_message.content,
                            "sender_id": user_id,
                            "room_id": room_id,
                            "created_at": chat_message.created_at.isoformat(),
                            "sender_username": chat_message.sender.username
                        },
                        room_id,
                        user_id
                    )
            except Exception as e:
                logger.error(f"Error in websocket loop: {e}")
            finally:
                manager.disconnect(room_id, user_id)
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error in websocket connection: {e}")
        await websocket.close(code=1008)

@router.get("/rooms/", status_code=200)
async def get_user_rooms(
    authorization: str = Header(...),
    db: Session = Depends(get_db)
):
    try:
        token = authorization.split(" ")[1]
        current_user = await get_current_user(token)
        user_id = int(current_user["id"])
        
        rooms = ChatService.get_user_rooms(db, user_id)
        return [{"id": room.id, "user1_id": room.user1_id, "user2_id": room.user2_id} for room in rooms]
    except Exception as e:
        logger.error(f"Erro ao listar salas: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))