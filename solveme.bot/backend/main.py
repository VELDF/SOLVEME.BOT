# solveme_bot/backend_users/main.py
import os
import logging
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

# Importa do database.py centralizado
# Note: load_dotenv não precisa estar aqui se database.py já o faz
from .database import engine, Base, get_db # Importa o 'engine' aqui
from . import models, schemas
from .src import user_manager, auth_utils

app = FastAPI(title="User Management API")

# --- CORREÇÃO AQUI: Mover Base.metadata.create_all para um evento de startup ---
@app.on_event("startup")
def startup_db_events():
    # Este evento será executado APENAS quando a aplicação FastAPI for iniciada por Uvicorn,
    # não quando os módulos são importados por PyTest.
    logging.info("Criando tabelas no banco de dados...")
    Base.metadata.create_all(bind=engine) # Usa o engine importado de database.py
    logging.info("Tabelas criadas com sucesso (ou já existentes).")

# --- Configuração de Logging para o Backend de Usuários ---
log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, "logs"))
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler(os.path.join(log_dir, "users_api.log")),
                        logging.StreamHandler()
                    ])

# --- Endpoints de Usuários (CRUD) ---

@app.post("/users/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def create_user_endpoint(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = user_manager.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email já registrado")
    
    hashed_password = auth_utils.get_password_hash(user.password)
    
    return user_manager.create_user(db=db, user=user, hashed_password=hashed_password)

@app.get("/users/", response_model=List[schemas.User])
def read_users_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = user_manager.get_users(db, skip=skip, limit=limit)
    return users

@app.get("/users/{user_id}", response_model=schemas.User)
def read_user_endpoint(user_id: int, db: Session = Depends(get_db)):
    db_user = user_manager.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
    return db_user

@app.put("/users/{user_id}", response_model=schemas.User)
def update_user_endpoint(user_id: int, user_update: schemas.UserUpdate, db: Session = Depends(get_db)):
    db_user = user_manager.update_user(db=db, user_id=user_id, user_update=user_update)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
    return db_user

@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_endpoint(user_id: int, db: Session = Depends(get_db)):
    success = user_manager.delete_user(db=db, user_id=user_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
    return {"message": "Usuário deletado com sucesso"}

@app.post("/users/{user_id}/change-password", status_code=status.HTTP_200_OK)
def change_password_endpoint(user_id: int, password_data: schemas.UserChangePassword, db: Session = Depends(get_db)):
    success = user_manager.change_user_password(
        db=db,
        user_id=user_id,
        old_password=password_data.old_password,
        new_password=password_data.new_password
    )
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Falha ao alterar senha (usuário ou senha antiga incorretos)")
    return {"message": "Senha alterada com sucesso"}