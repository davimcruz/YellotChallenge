from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from src.database.models import ChatRoom, UserModel
from src.domain.schemas import ChatRoomCreate

class ChatService:
    @staticmethod
    def create_room(db: Session, user1_id: int, room_data: ChatRoomCreate) -> ChatRoom:
        try:
            # Verifica se já existe uma sala entre os usuários
            existing_room = (
                db.query(ChatRoom)
                .filter(
                    ((ChatRoom.user1_id == user1_id) & (ChatRoom.user2_id == room_data.user2_id)) |
                    ((ChatRoom.user1_id == room_data.user2_id) & (ChatRoom.user2_id == user1_id))
                )
                .first()
            )
            
            if existing_room:
                return existing_room
            
            # Verifica se os usuários existem
            users = db.query(UserModel).filter(
                UserModel.id.in_([user1_id, room_data.user2_id])
            ).all()
            
            if len(users) != 2:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Um ou mais usuários não encontrados"
                )
            
            # Cria nova sala
            room = ChatRoom(
                user1_id=user1_id,
                user2_id=room_data.user2_id
            )
            
            db.add(room)
            db.commit()
            db.refresh(room)
            return room
            
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao criar sala de chat: {str(e)}"
            )