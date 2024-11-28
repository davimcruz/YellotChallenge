from fastapi import APIRouter, Depends, HTTPException, Header, WebSocket, status
from sqlalchemy.orm import Session
from src.database.connection import get_db
from src.services.auth_service import get_current_user
from src.services.chat_service import ChatService
from src.domain.schemas import ChatRoomCreate, ChatRoomResponse
from typing import List

router = APIRouter()

@router.post(
    "/rooms/", 
    response_model=ChatRoomResponse, 
    status_code=status.HTTP_201_CREATED
)
async def create_room(
    room_data: ChatRoomCreate,
    db: Session = Depends(get_db),
    authorization: str = Header(...)
):
    try:
        token = authorization.replace("Bearer ", "")
        current_user = await get_current_user(token)
        user_id = int(current_user["id"])
        
        room = ChatService.create_room(db, user_id, room_data)
        return room
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.websocket("/ws/{room_id}")
async def chat_websocket(
    websocket: WebSocket,
    room_id: int,
    token: str,
    db: Session = Depends(get_db)
):
    current_user = await get_current_user(token)
    user_id = int(current_user["id"])
    
    await manager.connect(websocket, room_id, user_id)
    
    try:
        while True:
            data = await websocket.receive_json()
            message_data = ChatMessageCreate(content=data["content"])
            
            message = ChatService.create_message(db, room_id, user_id, message_data)
            
            response = ChatMessageResponse(
                id=message.id,
                content=message.content,
                sender_id=message.sender_id,
                room_id=message.room_id,
                created_at=message.created_at,
                sender_username=message.sender.username
            )
            
            await manager.broadcast(
                response.model_dump(),
                room_id,
                user_id
            )
    except Exception as e:
        manager.disconnect(room_id, user_id)