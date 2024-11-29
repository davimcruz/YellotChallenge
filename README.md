# Chat API - YellotMob - Davi Machado

## Descrição

Este projeto é uma API de chat em tempo real desenvolvida como parte do desafio YellotMob, utilizando FastAPI, WebSockets e autenticação JWT. O sistema permite comunicação em tempo real entre dois usuários através de salas de chat privadas de dois usuários.

Importante: Projeto baseado em testes. Há um CI rodando por trás no GitHub Actions para garantir a qualidade do código baseado em testes automatizados.

## API em Produção

A API está disponível para testes em produção através do domínio:
```
https://api.davimachado.cloud
```

Você pode acessar a documentação interativa em:
- Swagger UI: `https://api.davimachado.cloud/docs`
- ReDoc: `https://api.davimachado.cloud/redoc`

Para testar o WebSocket em produção, use o protocolo `wss://`:
```
wss://api.davimachado.cloud/api/v1/chat/ws/{room_id}?token={seu_token}
```

## Estrutura do Projeto

- **src/**: Contém o código-fonte da aplicação.
  - **api/**: Define as rotas da API (auth e chat).
  - **services/**: Contém a lógica de negócios, serviços e gerenciamento de WebSocket.
  - **database/**: Configuração e modelos do banco de dados.
  - **domain/**: Modelos de domínio e DTOs.
- **tests/**: Contém testes automatizados.

## Decisões Arquiteturais

### FastAPI

- **FastAPI**: Escolhido para manter os requisitos do desafio.
- **SQLAlchemy**: ORM para abstração do banco de dados, facilitando a manutenção e mudança de SGBD.
- **Pydantic**: Validação de dados e serialização, garantindo integridade dos dados.
- **JWT**: Autenticação stateless, ideal para WebSockets e salvamento de sessão por id do usuário.

## Funcionalidades Principais

- Autenticação JWT
- Chat em tempo real via WebSocket
- Salas de chat privadas (2 usuários)
- Persistência de mensagens
- Interface web para teste

## Configuração

### Pré-requisitos

- Python 3.12.5
- PostgreSQL pronto para uso

### Instalação

1. Clone o repositório
2. Configure o ambiente virtual Python
3. Instale as dependências: `pip install -r requirements.txt`
4. Configure o arquivo `.env`:

```plaintext
DB_USER=seu_usuario
DB_PASSWORD=sua_senha
DB_HOST=localhost
DB_PORT=5432
DB_NAME=seu_banco_de_dados
SECRET_KEY=sua_chave_secreta
```

## Testando a Interface

1. Inicie o servidor FastAPI:

```plaintext
uvicorn src.main:app --reload --port 8001
```

2. Configure o arquivo `chat.js`:

- Substitua os tokens JWT:

```javascript
const token1 = "seu_token_usuario_1"
const token2 = "seu_token_usuario_2"
```

- Substitua os IDs dos usuários:

```javascript
const user1Id = 5 // ID do primeiro usuário
const user2Id = 6 // ID do segundo usuário
```

3. Abra o arquivo `index.html` no navegador

- A interface mostrará duas janelas de chat lado a lado
- O sistema tentará criar uma sala entre os usuários especificados
- Se a sala já existir, utilizará a sala existente
- As mensagens são exibidas em tempo real em ambas as janelas

## Endpoints da API

### Autenticação

- `POST /api/v1/users/`: Criar usuário
- `POST /api/v1/users/login`: Login e obtenção de token

### Chat

- `POST /api/v1/chat/rooms/`: Criar/obter sala
- `GET /api/v1/chat/rooms/{room_id}/messages`: Histórico de mensagens
- `WebSocket /api/v1/chat/ws/{room_id}`: Conexão WebSocket

## Segurança

- Tokens JWT com expiração
- Senhas hasheadas (bcrypt)
- Validação de usuários nas salas
- CORS configurado
- Proteção contra conexões WebSocket não autorizadas

## Melhorias Futuras

- Implementar reconexão automática do WebSocket
- Adicionar suporte a arquivos em geral com algum S3
- Adicionar indicador de "digitando..."
- Implementar sistema de leitura de mensagens (visualização)
- Retirar do PostgreSQL e utilizar algum noSQL + Redis para armazenamento das mensagens
