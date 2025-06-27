# C:\solveme.bot\backend_login\database.py

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from typing import Optional # <--- ESSENCIAL: Esta linha precisa estar presente para 'Optional'

load_dotenv() # Carrega variáveis de ambiente do arquivo .env

# Tenta obter a URL do banco de dados das variáveis de ambiente.
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# --- Definição da função create_db_engine ---
def create_db_engine(database_url: Optional[str] = None): # 'Optional' é usado aqui
    url = database_url if database_url else SQLALCHEMY_DATABASE_URL
    if not url:
        raise ValueError("DATABASE_URL não configurada no ambiente ou .env")
    
    print(f"DEBUG: create_db_engine foi chamada. Criando engine para URL: {url}")
    return create_engine(url)

print("DEBUG: O módulo database.py foi carregado. 'create_db_engine' e 'engine' devem estar definidos.")

# --- Criação da instância global 'engine' ---
engine = create_db_engine()

# Configuração para criação de sessões de banco de dados.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base declarativa para seus modelos SQLAlchemy.
Base = declarative_base()

# Função de dependência para obter uma sessão de banco de dados para as rotas FastAPI.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()