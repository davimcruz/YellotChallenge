from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente
load_dotenv()

def test_connection():
    # Obtém a URL do banco de dados a partir das variáveis de ambiente
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    try:
        # Cria uma engine de conexão com o banco de dados
        engine = create_engine(DATABASE_URL)
        with engine.connect() as connection:
            print("Conexão estabelecida com sucesso")
            return True
    except Exception as e:
        print(f"Erro ao conectar: {str(e)}")
        return False

if __name__ == "__main__":
    test_connection()