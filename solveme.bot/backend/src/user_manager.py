from sqlalchemy.orm import Session
from typing import List, Optional
# Importações relativas para módulos no mesmo nível do pacote 'backend'
from .. import crud, models, schemas 
# CORRIGIDO: Importa get_password_hash e verify_password com seus nomes CORRETOS
from .auth_utils import get_password_hash, verify_password 
from backend.src import auth_utils

def create_new_user(db: Session, user_data: schemas.UserCreate) -> models.Usuario: 
    """
    Cria um novo usuário, hasheando a senha antes de salvar.
    """
    # CORRIGIDO: Chamar get_password_hash
    hashed_password = get_password_hash(user_data.password) 
    return crud.create_user(db=db, user=user_data, hashed_password=hashed_password)

# Função para autenticar um usuário
def authenticate_user(db: Session, email: str, password: str) -> Optional[models.Usuario]: 
    """
    Autentica um usuário pelo email e senha.
    Retorna o objeto do usuário se as credenciais forem válidas, None caso contrário.
    """
    user = crud.get_user_by_email(db, email) 
    if not user or not verify_password(password, user.senha_hash):
        return None
    return user

# Função para obter todos os usuários
def get_all_users(db: Session, skip: int = 0, limit: int = 100) -> List[models.Usuario]: 
    """
    Retorna uma lista de todos os usuários.
    """
    return crud.get_users(db, skip=skip, limit=limit) 

# Função para obter um usuário por ID
def get_user_by_id(db: Session, user_id: int) -> Optional[models.Usuario]: 
    """
    Retorna um usuário pelo seu ID.
    """
    return crud.get_user(db, user_id) 

# Função para atualizar um usuário existente
def update_existing_user(db: Session, user_id: int, user_update_data: schemas.UserUpdate) -> Optional[models.Usuario]: 
    """
    Atualiza os dados de um usuário existente.
    """
    db_user = crud.get_user(db, user_id) 
    if not db_user:
        return None
    return crud.update_user(db=db, db_user=db_user, user_update=user_update_data)

# Função para alterar a senha de um usuário
def change_user_password(db: Session, user_id: int, old_password: str, new_password: str) -> Optional[models.Usuario]: 
    """
    Altera a senha de um usuário, verificando a senha antiga.
    """
    db_user = crud.get_user(db, user_id) 
    if not db_user:
        return None
    
    if not verify_password(old_password, db_user.senha_hash):
        return None # Senha antiga incorreta

    # CORRIGIDO: Chamar get_password_hash
    hashed_new_password = get_password_hash(new_password) 
    return crud.update_user_password(db, db_user, hashed_new_password)

# Função para deletar um usuário
def delete_user_by_id(db: Session, user_id: int) -> bool:
    """
    Deleta um usuário pelo seu ID.
    """
    return crud.delete_user(db, user_id)