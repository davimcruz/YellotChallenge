import logging
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from src.database.models import ChatRoom, ChatMessage, UserModel
from src.domain.schemas import ChatRoomCreate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatService:
    @staticmethod
    def get_room(db: Session, room_id: int, user_id: int) -> ChatRoom:
        try:
            logger.info(f"Buscando sala {room_id} para usuário {user_id}")
            room = db.query(ChatRoom).filter(ChatRoom.id == room_id).first()
            
            if not room:
                logger.warning(f"Sala {room_id} não encontrada")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Sala não encontrada"
                )
            
            if room.user1_id != user_id and room.user2_id != user_id:
                logger.warning(f"Usuário {user_id} não pertence à sala {room_id}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Usuário não pertence a esta sala"
                )
            
            logger.info(f"Sala {room_id} encontrada com sucesso")
            return room
        except Exception as e:
            logger.error(f"Erro ao buscar sala: {str(e)}")
            raise

    @staticmethod
    def create_room(db: Session, user1_id: int, user2_id: int) -> ChatRoom:
        try:
            # Verificar sala existente
            existing_room = (
                db.query(ChatRoom)
                .filter(
                    ((ChatRoom.user1_id == user1_id) & (ChatRoom.user2_id == user2_id)) |
                    ((ChatRoom.user1_id == user2_id) & (ChatRoom.user2_id == user1_id))
                )
                .first()
            )
            
            if existing_room:
                return existing_room
            
            room = ChatRoom(
                user1_id=user1_id,
                user2_id=user2_id
            )
            
            db.add(room)
            db.commit()
            db.refresh(room)
            return room
            
        except Exception as e:
            db.rollback()
            raise e

    @staticmethod
    def create_message(db: Session, room_id: int, user_id: int, content: str) -> ChatMessage:
        try:
            logger.info(f"Criando mensagem na sala {room_id} pelo usuário {user_id}")
            
            # Primeiro verifica se o usuário tem acesso à sala
            room = ChatService.get_room(db, room_id, user_id)
            
            message = ChatMessage(
                content=content,
                sender_id=user_id,
                room_id=room_id
            )
            
            db.add(message)
            db.commit()
            db.refresh(message)
            
            logger.info(f"Mensagem {message.id} criada com sucesso")
            return message
            
        except Exception as e:
            logger.error(f"Erro ao criar mensagem: {str(e)}")
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao criar mensagem"
            )

    @staticmethod
    def get_room_messages(db: Session, room_id: int, user_id: int):
        try:
            logger.info(f"Buscando mensagens da sala {room_id}")
            room = ChatService.get_room(db, room_id, user_id)
            
            messages = (
                db.query(ChatMessage)
                .filter(ChatMessage.room_id == room_id)
                .order_by(ChatMessage.created_at.asc())
                .all()
            )
            
            logger.info(f"Encontradas {len(messages)} mensagens")
            return messages
        except Exception as e:
            logger.error(f"Erro ao buscar mensagens: {str(e)}")
            raise

    @staticmethod
    def get_user_rooms(db: Session, user_id: int):
        return db.query(ChatRoom).filter(
            (ChatRoom.user1_id == user_id) | (ChatRoom.user2_id == user_id)
        ).all()