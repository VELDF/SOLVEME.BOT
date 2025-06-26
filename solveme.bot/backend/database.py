# --- NOVO ARQUIVO: database.py ---

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
print(f"DEBUG: DATABASE_URL lida de .env: {SQLALCHEMY_DATABASE_URL}") # <--- ADICIONE ESTA LINHA PARA DEPURAR

if not SQLALCHEMY_DATABASE_URL:
    raise ValueError("DATABASE_URL não configurado no arquivo .env")

# Cria o motor de banco de dados SQLAlchemy.
# `pool_pre_ping=True` ajuda a manter as conexões ativas e a reconectar se necessário.
engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)

# Cria uma SessionLocal class
# Cada instância da SessionLocal será uma sessão de banco de dados.
# O `autocommit=False` significa que você precisará commitar suas transações explicitamente.
# O `autoflush=False` significa que as operações não serão salvas no banco de dados automaticamente antes de um commit.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para os modelos declarativos do SQLAlchemy.
# Os modelos de banco de dados herdarão desta classe.
Base = declarative_base()

# Função de utilidade para obter uma sessão de banco de dados.
# Esta é uma "dependência" que o FastAPI usará para injetar uma sessão
# de banco de dados em suas funções de rota.
def get_db():
    db = SessionLocal() # Cria uma nova sessão
    try:
        yield db # Retorna a sessão para o chamador
    finally:
        db.close() # Garante que a sessão seja fechada após o uso