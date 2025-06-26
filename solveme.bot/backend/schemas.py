# --- NOVO ARQUIVO: schemas.py ---

from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List

# Esquema base para a requisição de chat
class ChatRequest(BaseModel):
    prompt: str
    history: List[dict] = [] # Lista de dicionários para o histórico da conversa

# Esquemas para Usuário (exemplo, você precisará de mais para registro/login)
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    nome: str
    telefone: str
    setor: str
    password: str # A senha em texto puro antes de ser hasheada

class UserResponse(UserBase):
    id: int
    nome: str
    telefone: str
    setor: str
    eh_admin: bool
    ativo: bool
    criado_em: datetime

    class Config:
        orm_mode = True # Habilita o modo ORM para Pydantic (compatibilidade com SQLAlchemy)

# Esquemas para Mensagens de Chat
class ChatMessageBase(BaseModel):
    sender: str # Poderia ser um Enum('USER', 'AI') aqui também
    content: str
    attachment_url: Optional[str] = None

class ChatMessageCreate(ChatMessageBase):
    pass # No momento da criação, os campos são os mesmos da base

class ChatMessageResponse(ChatMessageBase):
    id: int
    conversation_id: int
    created_at: datetime

    class Config:
        orm_mode = True

# Esquemas para Conversas de Chat
class ChatConversationBase(BaseModel):
    title: Optional[str] = None

class ChatConversationCreate(ChatConversationBase):
    user_id: int

class ChatConversationResponse(ChatConversationBase):
    id: int
    user_id: int
    created_at: datetime
    messages: List[ChatMessageResponse] = [] # Opcional: incluir mensagens ao listar conversas

    class Config:
        orm_mode = True