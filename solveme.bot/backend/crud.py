# --- NOVO ARQUIVO: crud.py ---

from sqlalchemy.orm import Session
from . import models, schemas
from typing import Optional

# Funções CRUD para Usuário
def get_user_by_email(db: Session, email: str):
    return db.query(models.Usuario).filter(models.Usuario.email == email).first()

def create_user(db: Session, user: schemas.UserCreate, hashed_password: str):
    # Nota: eh_admin e ativo não estão no UserCreate do schemas.py,
    # então adicionei a lógica para caso você os adicione posteriormente ou precise de valores padrão.
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

# Funções CRUD para Mensagens de Chat
def create_chat_conversation(db: Session, user_id: int, title: Optional[str] = None):
    db_conversation = models.ChatConversation(user_id=user_id, title=title)
    db.add(db_conversation)
    db.commit()
    db.refresh(db_conversation)
    return db_conversation

def get_chat_conversation(db: Session, conversation_id: int):
    return db.query(models.ChatConversation).filter(models.ChatConversation.id == conversation_id).first()

def create_chat_message(db: Session, conversation_id: int, sender: str, content: str, attachment_url: Optional[str] = None):
    db_message = models.ChatMessage(
        conversation_id=conversation_id,
        sender=sender,
        content=content,
        attachment_url=attachment_url
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def get_chat_messages(db: Session, conversation_id: int):
    return db.query(models.ChatMessage).filter(models.ChatMessage.conversation_id == conversation_id).order_by(models.ChatMessage.created_at).all()

# Você adicionaria mais funções CRUD aqui para Notes, Feedbacks, etc., conforme necessário.