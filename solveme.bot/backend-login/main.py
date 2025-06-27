import os
import logging
from fastapi import FastAPI, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from typing import List, Optional

# Importações dos módulos no mesmo nível do pacote 'backend'
from .database import engine, Base, get_db
from . import models, schemas, crud 

# Importa user_manager usando caminho absoluto do pacote 'backend.src'
from backend.src import user_manager 

# Carrega variáveis de ambiente (do .env na raiz do projeto)
load_dotenv()

# Configurações do logger (para ver logs no terminal)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI(
    title="Backend User Management API",
    description="API para gerenciar usuários no sistema Solveme.Bot",
    version="1.0.0",
)

# Evento de inicialização: Cria as tabelas no DB se não existirem
@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)
    logging.info("Tabelas do banco de dados (para Backend) criadas/verificadas.")

# Endpoint de teste básico
@app.get("/")
async def read_root():
    return {"message": "Backend User Management API is running!"}

# --- ENDPOINTS CRUD DE USUÁRIO ---

# Endpoint para registrar um novo usuário
@app.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Usa crud.get_user_by_email para verificar duplicidade
    db_user = crud.get_user_by_email(db, email=user.email) 
    if db_user:
        raise HTTPException(status_code=400, detail="Email já registrado")
    
    # Chama user_manager para criar o novo usuário
    return user_manager.create_new_user(db=db, user_data=user)

# Endpoint para login do usuário (autenticação)
@app.post("/login", response_model=schemas.UserResponse) 
async def login_user(form_data: schemas.UserCreate, db: Session = Depends(get_db)): 
    user = user_manager.authenticate_user(db, form_data.email, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

# Endpoint para listar todos os usuários
@app.get("/users/", response_model=List[schemas.UserResponse])
async def read_users_api(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = user_manager.get_all_users(db, skip=skip, limit=limit)
    return users

# Endpoint para obter um usuário por ID
@app.get("/users/{user_id}", response_model=schemas.UserResponse)
async def read_user_api(user_id: int, db: Session = Depends(get_db)):
    db_user = user_manager.get_user_by_id(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return db_user

# Endpoint para atualizar um usuário (parcialmente ou totalmente)
@app.put("/users/{user_id}", response_model=schemas.UserResponse)
async def update_user_api(user_id: int, user_update: schemas.UserUpdate, db: Session = Depends(get_db)):
    db_user = user_manager.update_existing_user(db, user_id, user_update)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return db_user

# Endpoint para alterar a senha de um usuário
@app.post("/users/{user_id}/change-password", status_code=status.HTTP_200_OK)
async def change_password_api(user_id: int, passwords: dict, db: Session = Depends(get_db)):
    old_password = passwords.get("old_password")
    new_password = passwords.get("new_password")

    if not old_password or not new_password:
        raise HTTPException(status_code=400, detail="Senha antiga e nova senha são obrigatórias.")

    updated_user = user_manager.change_user_password(db, user_id, old_password, new_password)
    if not updated_user: 
        raise HTTPException(status_code=400, detail="Falha ao alterar senha (usuário ou senha antiga incorretos)")
    
    return {"message": "Senha alterada com sucesso"}

# Endpoint para deletar um usuário
@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_api(user_id: int, db: Session = Depends(get_db)):
    deleted = user_manager.delete_user_by_id(db, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return Response(status_code=status.HTTP_204_NO_CONTENT)