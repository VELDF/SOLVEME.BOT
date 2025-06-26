# SOLVEME.BOT/backend/schemas.py

from pydantic import BaseModel, EmailStr, ConfigDict # ADICIONADO: ConfigDict
from datetime import datetime
from typing import Optional, List

# Esquema base para a requisição de chat (se você ainda o usa aqui, se não, pode remover)
class ChatRequest(BaseModel):
    prompt: str
    history: List[dict] = []

# Esquemas para Usuário
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

    model_config = ConfigDict(from_attributes=True) # Corrigido para Pydantic V2

# Esquemas para Mensagens de Chat (se você ainda os usa aqui)
class ChatMessageBase(BaseModel):
    sender: str
    content: str
    attachment_url: Optional[str] = None

class ChatMessageCreate(ChatMessageBase):
    pass

class ChatMessageResponse(ChatMessageBase):
    id: int
    conversation_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True) # Corrigido para Pydantic V2

# Esquemas para Conversas de Chat (se você ainda os usa aqui)
class ChatConversationBase(BaseModel):
    title: Optional[str] = None

class ChatConversationCreate(ChatConversationBase):
    user_id: int

class ChatConversationResponse(ChatConversationBase):
    id: int
    user_id: int
    created_at: datetime
    messages: List[ChatMessageResponse] = []

    model_config = ConfigDict(from_attributes=True) # Corrigido para Pydantic V2

# ADICIONADO/CORRIGIDO: Schema para atualização de usuário (permite campos opcionais)
class UserUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[EmailStr] = None
    telefone: Optional[str] = None
    setor: Optional[str] = None
    eh_admin: Optional[bool] = None
    ativo: Optional[bool] = None
    
    model_config = ConfigDict(from_attributes=True) # Corrigido para Pydantic V2