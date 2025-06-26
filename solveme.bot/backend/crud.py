from sqlalchemy.orm import Session
from sqlalchemy import select # Importante para as queries no SQLAlchemy 1.4+ / 2.0
from . import models, schemas # Importa os modelos e schemas do mesmo nível
from typing import Optional, List

# --- Funções CRUD para o modelo Usuario ---

def get_user_by_email(db: Session, email: str):
    """
    Busca um usuário pelo email.
    """
    return db.execute(select(models.Usuario).filter(models.Usuario.email == email)).scalar_one_or_none()

def create_user(db: Session, user: schemas.UserCreate, hashed_password: str):
    """
    Cria um novo usuário no banco de dados.
    """
    db_user = models.Usuario(
        nome=user.nome,
        email=user.email,
        telefone=user.telefone,
        setor=user.setor,
        senha_hash=hashed_password,
        eh_admin=user.eh_admin if hasattr(user, 'eh_admin') else False,
        ativo=user.ativo if hasattr(user, 'ativo') else True
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[models.Usuario]:
    """
    Retorna uma lista de todos os usuários, com paginação opcional.
    """
    return db.execute(select(models.Usuario).offset(skip).limit(limit)).scalars().all()

def get_user(db: Session, user_id: int) -> Optional[models.Usuario]:
    """
    Retorna um usuário pelo seu ID.
    """
    return db.execute(select(models.Usuario).filter(models.Usuario.id == user_id)).scalar_one_or_none()

def update_user(db: Session, db_user: models.Usuario, user_update: schemas.UserUpdate):
    """
    Atualiza os dados de um usuário existente.
    """
    update_data = user_update.model_dump(exclude_unset=True) # Pega apenas os campos que foram enviados no update
    for key, value in update_data.items():
        setattr(db_user, key, value)
    db.add(db_user) # Adiciona para garantir que o SQLAlchemy rastreie a mudança
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int) -> bool:
    """
    Deleta um usuário pelo seu ID.
    """
    db_user = db.execute(select(models.Usuario).filter(models.Usuario.id == user_id)).scalar_one_or_none()
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False

def update_user_password(db: Session, db_user: models.Usuario, hashed_password: str):
    """
    Atualiza apenas o hash da senha de um usuário.
    """
    db_user.senha_hash = hashed_password
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user