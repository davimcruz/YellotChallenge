# Chat API - YellotMob

## Descrição

Este projeto é uma API de chat em tempo real desenvolvida como parte do desafio YellotMob, utilizando FastAPI, WebSockets e autenticação JWT.

## Estrutura do Projeto

- **src/**: Contém o código-fonte da aplicação.

  - **api/**: Define as rotas da API (auth e chat).
  - **services/**: Contém a lógica de negócios, serviços e gerenciamento de WebSocket.
  - **database/**: Configuração e modelos do banco de dados.
  - **domain/**: Modelos de domínio e DTOs.

- **tests/**: Contém testes automatizados para autenticação e chat.

## Funcionalidades Principais

- Autenticação JWT
- Criação e gestão de usuários
- Chat em tempo real via WebSocket
- Salas de chat privadas (2 usuários por sala)
- Persistência de mensagens
- Testes automatizados

## Configuração

### Pré-requisitos

- Python 3.12.5
- PostgreSQL
- Ambiente virtual Python

### Instalação

1. Clone o repositório:

```bash
git clone https://github.com/davimcruz/YellotChallenge.git
```

2. Crie e ative um ambiente virtual:

```bash
python -m venv venv
source venv/bin/activate
```

3. Instale as dependências:

```bash
pip install -r requirements.txt
```

4. Configure o arquivo `.env`:

```plaintext
DB_USER=seu_usuario
DB_PASSWORD=sua_senha
DB_HOST=seu_host
DB_PORT=5432
DB_NAME=nome_do_banco
SECRET_KEY=secret_key
```

## Endpoints da API

### Autenticação

- `POST /api/v1/users/` - Criar novo usuário
- `POST /api/v1/users/login` - Autenticar usuário e receber token JWT

### Chat

- `POST /api/v1/chat/rooms/` - Criar nova sala de chat
- `GET /api/v1/chat/rooms/` - Listar salas do usuário
- `WebSocket /api/v1/chat/ws/{room_id}` - Conectar ao chat em tempo real

## Uso do Chat

1. Criar usuários:

```bash
curl -X POST http://localhost:8001/api/v1/users/ \
  -H "Content-Type: application/json" \
  -d '{"username": "user1", "email": "user1@example.com", "password": "password123"}'
```

2. Fazer login e obter token:

```bash
curl -X POST http://localhost:8001/api/v1/users/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user1@example.com", "password": "password123"}'
```

3. Criar sala de chat:

```bash
curl -X POST http://localhost:8001/api/v1/chat/rooms/ \
  -H "Authorization: Bearer {seu_token}" \
  -H "Content-Type: application/json" \
  -d '{"user2_id": 2}'
```

4. Conectar ao WebSocket:

```javascript
const ws = new WebSocket(
  "ws://localhost:8001/api/v1/chat/ws/{room_id}?token={seu_token}"
)
```

## Testes

O projeto inclui testes automatizados para todas as funcionalidades:

- Testes de autenticação
- Testes de criação de usuários
- Testes de salas de chat
- Testes de WebSocket

Execute os testes com:

```bash
pytest -v
```

Para testes específicos:

```bash
pytest tests/test_auth.py -v  # Testar a autenticação
pytest tests/test_chat.py -v  # Testar funções de chat
```

## Documentação da API

- Swagger UI: [http://localhost:8001/docs](http://localhost:8001/docs)
- ReDoc: [http://localhost:8001/redoc](http://localhost:8001/redoc)

## Segurança

- Tokens JWT para autenticação
- Senhas hasheadas com bcrypt
- Validação de usuários nas salas de chat
- Proteção contra conexões WebSocket não autorizadas
