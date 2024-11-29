from fastapi import APIRouter, Depends, WebSocket, HTTPException, status, Header
from sqlalchemy.orm import Session
from src.database.connection import get_db
from src.services.auth_service import get_current_user
from src.services.chat_service import ChatService
from src.services.websocket_manager import manager
from pydantic import BaseModel
import logging
import json
from typing import List
from src.domain.models import Message
from datetime import datetime
from src.database.models import UserModel
from pytz import timezone

router = APIRouter()
logger = logging.getLogger(__name__)

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
        
        # Verificar se os usuários existem de fato no banco
        user2 = db.query(UserModel).filter(UserModel.id == room.user2_id).first()
        if not user2:
            raise HTTPException(status_code=404, detail="Usuário 2 não encontrado")
        
        # Verificar se a sala já existe
        existing_room = ChatService.get_existing_room(db, user1_id, room.user2_id)
        if existing_room:
            return {
                "id": existing_room.id,
                "user1_id": existing_room.user1_id,
                "user2_id": existing_room.user2_id
            }
        
        # Criar nova sala
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
    # Chama o websocket para comunicação em tempo real em uma sala de chat

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
                    
                    # Cria a mensagem e salva no banco de dados
                    chat_message = ChatService.create_message(
                        db=db,
                        room_id=room_id,
                        user_id=user_id,
                        content=message.get("content", "")
                    )
                    
                    # Envia a mensagem para todos os usuários na sala, incluindo o remetente
                    await manager.broadcast(
                        {
                            "id": chat_message.id,
                            "content": chat_message.content,
                            "sender_id": user_id,
                            "room_id": room_id,
                            "created_at": chat_message.created_at.isoformat() if chat_message.created_at else None,
                            "sender_username": chat_message.sender.username
                        },
                        room_id
                    )
            except Exception as e:
                logger.error(f"Erro no loop do websocket: {e}")
            finally:
                manager.disconnect(room_id, user_id)
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Erro na conexão websocket: {e}")
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
@router.get("/rooms/{room_id}/messages", response_model=List[Message])
async def get_messages(room_id: int, db: Session = Depends(get_db)):
    messages = ChatService.get_messages_by_room(db, room_id)
    response = []
    for message in messages:
        sender = db.query(UserModel).filter(UserModel.id == message.sender_id).first()
        created_at = message.created_at.astimezone(timezone('America/Sao_Paulo')).isoformat() if message.created_at else None
        response.append({
            "content": message.content,
            "sender_username": sender.username,
            "created_at": created_at
        })
    return response