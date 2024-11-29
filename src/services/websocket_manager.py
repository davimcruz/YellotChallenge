from fastapi import WebSocket
from typing import Dict

class ConnectionManager:
    def __init__(self):
        # Dicionário que irá armazena as conexões ativas dentro do websocket
        # A estrutura é um dicionário de dicionários, onde a chave externa é o ID da sala (o que faz sentido, mesmo que seja um chat privado)
        # e a chave interna é o ID do usuário, com o valor sendo a conexão websocket
        self.active_connections: Dict[int, Dict[int, WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room_id: int, user_id: int):
        # Aceita a conexão websocket do cliente
        await websocket.accept()
        # Se a sala ainda não tiver conexões ativas, inicializa um novo dicionário para ela (referencia ao dicionário de conexões)
        if room_id not in self.active_connections:
            self.active_connections[room_id] = {}
        # Armazena a conexão websocket do usuário na sala correspondente
        self.active_connections[room_id][user_id] = websocket

    def disconnect(self, room_id: int, user_id: int):
        # Remove a conexão do usuário da sala especificada pra quando o usuario se desconectar
        if room_id in self.active_connections:
            self.active_connections[room_id].pop(user_id, None)

    async def broadcast(self, message: dict, room_id: int, sender_id: int):
        # Envia uma mensagem para todos os usuários na sala, exceto o remetente (evitar redundancia de mensagens)
        # Isso é útil para enviar mensagens de chat para todos os participantes de uma sala (o que no futuro pode ser expandido para mais de 2 usuários, tal como grupos)
        if room_id in self.active_connections:
            for user_id, connection in self.active_connections[room_id].items():
                if user_id != sender_id:
                    await connection.send_json(message)

manager = ConnectionManager()

__all__ = ['manager']