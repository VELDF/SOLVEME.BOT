# solveme_bot/backend_users/src/user_manager.py
from sqlalchemy.orm import Session
from sqlalchemy import select # <--- ADICIONADO: Importar select para consultas SQLAlchemy 2.0
from .. import models, schemas # Importa modelos e schemas do nível acima
from . import auth_utils # Importa auth_utils para hashing
from typing import List, Optional # Importado Optional e List para type hints

# Função para obter um usuário pelo ID
def get_user(db: Session, user_id: int):
    # CORREÇÃO: Usar select() e db.scalar() para SQLAlchemy 2.0
    return db.scalar(select(models.User).filter(models.User.id == user_id))

# Função para obter um usuário pelo email
def get_user_by_email(db: Session, email: str):
    # CORREÇÃO: Usar select() e db.scalar() para SQLAlchemy 2.0
    return db.scalar(select(models.User).filter(models.User.email == email))

# Função para obter múltiplos usuários (com paginação básica)
# CORREÇÃO: Removido o parâmetro 'status' que causava AttributeError
def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[models.User]:
    # CORREÇÃO: Usar select() para consultas SQLAlchemy 2.0
    query = select(models.User)
    # Se você tivesse filtros específicos para usuários (ex: por nome, email), eles viriam aqui
    
    return db.scalars(query.offset(skip).limit(limit)).all()

# Função para criar um novo usuário
def create_user(db: Session, user: schemas.UserCreate, hashed_password: str) -> models.User:
    db_user = models.User(
        email=user.email,
        hashed_password=hashed_password,
        name=user.name,
        role=user.role,
        phone=user.phone
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Função para atualizar um usuário (já lida com campos opcionais)
def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate) -> Optional[models.User]:
    # CORREÇÃO: Usar select() e db.scalar() para encontrar o usuário
    db_user = db.scalar(select(models.User).filter(models.User.id == user_id))
    if db_user:
        update_data = user_update.model_dump(exclude_unset=True) # Usa model_dump() de Pydantic v2
        update_data.pop("password", None) # Garante que a senha não seja atualizada diretamente aqui

        for key, value in update_data.items():
            setattr(db_user, key, value)
        db.commit()
        db.refresh(db_user)
    return db_user

# Função para deletar um usuário
def delete_user(db: Session, user_id: int) -> bool:
    # CORREÇÃO: Usar select() e db.scalar() para encontrar o usuário
    db_user = db.scalar(select(models.User).filter(models.User.id == user_id))
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False

# Função para alterar senha
def change_user_password(db: Session, user_id: int, old_password: str, new_password: str) -> bool:
    # CORREÇÃO: Usar select() e db.scalar() para encontrar o usuário
    db_user = db.scalar(select(models.User).filter(models.User.id == user_id))
    if not db_user:
        return False # Usuário não encontrado

    if not auth_utils.verify_password(old_password, db_user.hashed_password):
        return False # Senha antiga incorreta

    db_user.hashed_password = auth_utils.get_password_hash(new_password)
    db.commit()
    db.refresh(db_user)
    return True