# Chat API - YellotMob

## Descrição

Este projeto é uma API de chat desenvolvida como parte do desafio YellotMob.

## Estrutura do Projeto

- **src/**: Contém o código-fonte da aplicação.

  - **api/**: Define as rotas da API.
  - **services/**: Contém a lógica de negócios e serviços.
  - **database/**: Configuração e modelos do banco de dados.
  - **domain/**: Modelos de domínio e DTOs.

- **tests/**: Contém testes automatizados para a aplicação.

## Configuração

### Pré-requisitos

- Python 3.12.5
- PostgreSQL

### Instalação

1. Clone o repositório:

   ```bash
   git clone https://github.com/davimcruz/YellotChallenge.git
   ```

2. Crie e ative um ambiente virtual:

   ```bash
   python -m venv venv
   source venv/bin/activate  # No Windows use `venv\Scripts\activate`
   ```

3. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

4. Configure o arquivo `.env` com suas credenciais:
   ```plaintext
   DB_USER=seu_usuario
   DB_PASSWORD=sua_senha
   DB_HOST=seu_host
   DB_PORT=5432
   DB_NAME=nome_do_banco
   SECRET_KEY=sua_secret_key
   ```

### Banco de Dados

O sistema utiliza SQLAlchemy como ORM e as tabelas são criadas automaticamente na primeira execução da aplicação. Não será necessário executar migrações manualmente.

### Docker

Se optar por usar Docker (um dos requisitos não funcionais do desafio), observe que pode ser necessário ajustar:
- Portas expostas no container
- Network
- Variáveis de ambiente

Mantenha as mesmas variáveis do arquivo `.env` para desenvolvimento local ao configurar o ambiente Docker.

### Teste de Conexão

Antes de iniciar a API, é importante verificar se a conexão com o seu banco está funcionando:

```bash
# Execute o teste de conexão
python src/tests/test_connection.py

# Se aparecer "Conexão estabelecida com sucesso", pode prosseguir
# Caso contrário, verifique suas configurações no .env
```

## Uso

### Executando com Docker

```bash
docker-compose up --build
```

### Executando Localmente

Inicie o servidor FastAPI:

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8001
```

### Documentação da API

- Swagger UI: [http://localhost:8001/docs](http://localhost:8001/docs)
- ReDoc: [http://localhost:8001/redoc](http://localhost:8001/redoc)

### Endpoints Principais

- `POST /api/v1/users/` - Criar novo usuário
- `POST /api/v1/login/` - Autenticar usuário
- `GET /api/v1/users/` - Listar usuários

### Testes e CI

O projeto utiliza GitHub Actions para Integração Contínua (CI). A cada push ou pull request:
- Testes automatizados são executados
- A cobertura de código é verificada
- Os resultados são disponibilizados na aba Actions do GitHub

Para executar os testes localmente:

```bash
pytest
```
