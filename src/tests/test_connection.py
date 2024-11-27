from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
import psycopg2

# Carrega env vars
load_dotenv()

def test_connection():
    try:
        # Usa as mesmas configs do .env pra garantir consistência
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )
        conn.close()
        print("Conexão estabelecida com sucesso")
        return True
    except Exception as e:
        print(f"Erro ao conectar: {str(e)}")
        return False

# Roda o teste direto se executar o arquivo
if __name__ == "__main__":
    test_connection()