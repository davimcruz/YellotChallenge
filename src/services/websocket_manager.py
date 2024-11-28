from fastapi import WebSocket
from typing import Dict

class ConnectionManager:
    def __init__(self):
        # Aqui a gente guarda todas as conexões ativas
        # É como um dicionário de dicionários onde:
        # - A chave externa é o ID da sala
        # - A chave interna é o ID do usuário 
        # - O valor é a conexão WebSocket dele
        self.active_connections: Dict[int, Dict[int, WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room_id: int, user_id: int):
        # Aceitamos a conexão dele
        await websocket.accept()
        
        # Se a sala não existe ainda, criamos ela
        if room_id not in self.active_connections:
            self.active_connections[room_id] = {}
            
        # Guardamos a conexão do usuário naquela sala
        self.active_connections[room_id][user_id] = websocket

    def disconnect(self, room_id: int, user_id: int):
        # Quando alguém desconecta:
        # Se a sala existe, removemos o usuário dela
        if room_id in self.active_connections:
            self.active_connections[room_id].pop(user_id, None)
            
            # Se a sala ficou vazia, removemos ela também
            # Pra não ficar ocupando memória à toa
            if not self.active_connections[room_id]:
                self.active_connections.pop(room_id)

    async def broadcast(self, message: dict, room_id: int, sender_id: int):
        # Quando alguém manda mensagem:
        # Verificamos se a sala existe
        if room_id in self.active_connections:
            # Mandamos a mensagem pra todo mundo da sala (que no caso são apenas 2 usuários)
            # exceto pra quem enviou (por isso o if user_id != sender_id)
            for user_id, connection in self.active_connections[room_id].items():
                if user_id != sender_id:
                    await connection.send_json(message)

# Criamos uma única instância do gerenciador
# que vai ser usada em toda a aplicação
manager = ConnectionManager()