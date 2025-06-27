# --- NOVO ARQUIVO: models.py ---

from sqlalchemy import Boolean, Column, Integer, String, TIMESTAMP, Text, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base # Importa a Base que definimos em database.py

# Modelo para a tabela 'usuarios'
class Usuario(Base):
    __tablename__ = "usuarios" # Nome da tabela no banco de dados

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(250), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    telefone = Column(String(16), nullable=False)
    setor = Column(String(100), nullable=False)
    senha_hash = Column(String(255), nullable=False)
    eh_admin = Column(Boolean, default=False, nullable=False)
    ativo = Column(Boolean, default=True, nullable=False)
    criado_em = Column(TIMESTAMP, default=func.now(), nullable=False)

    # Relacionamentos para outras tabelas (opcional, mas bom para ORM)
    tokens_recuperacao = relationship("TokenRecuperacao", back_populates="usuario")
    logins = relationship("Login", back_populates="usuario")
    notes = relationship("Note", back_populates="user")
    feedbacks = relationship("Feedback", back_populates="user")
    chat_conversations = relationship("ChatConversation", back_populates="user")

# Modelo para a tabela 'tokens_recuperacao'
class TokenRecuperacao(Base):
    __tablename__ = "tokens_recuperacao"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    codigo = Column(String(6), nullable=False)
    expiracao = Column(TIMESTAMP, nullable=False)
    usado = Column(Boolean, default=False, nullable=False)
    criado_em = Column(TIMESTAMP, default=func.now(), nullable=False)

    usuario = relationship("Usuario", back_populates="tokens_recuperacao")

# Modelo para a tabela 'logins'
class Login(Base):
    __tablename__ = "logins"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    data_login = Column(TIMESTAMP, default=func.now(), nullable=False)
    ip_address = Column(String(45), nullable=True) # Pode ser NULL
    sucesso = Column(Boolean, nullable=False)

    usuario = relationship("Usuario", back_populates="logins")

# Modelo para a tabela 'notes'
class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=True)
    content = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("Usuario", back_populates="notes")

# Modelo para a tabela 'feedbacks'
class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True) # Pode ser NULL
    type = Column(Enum("PROBLEMA", "IDEIA", "OUTRO"), nullable=False)
    message = Column(Text, nullable=False)
    status = Column(Enum("ABERTO", "EM_ANALISE", "CONCLUIDO"), default="ABERTO", nullable=False)
    created_at = Column(TIMESTAMP, default=func.now(), nullable=False)

    user = relationship("Usuario", back_populates="feedbacks")
    attachments = relationship("FeedbackAttachment", back_populates="feedback")

# Modelo para a tabela 'feedback_attachments'
class FeedbackAttachment(Base):
    __tablename__ = "feedback_attachments"

    id = Column(Integer, primary_key=True, index=True)
    feedback_id = Column(Integer, ForeignKey("feedbacks.id", ondelete="CASCADE"), nullable=False)
    file_url = Column(String(1024), nullable=False)
    file_type = Column(String(100), nullable=True)
    created_at = Column(TIMESTAMP, default=func.now(), nullable=False)

    feedback = relationship("Feedback", back_populates="attachments")

# Modelo para a tabela 'chat_conversations'
class ChatConversation(Base):
    __tablename__ = "chat_conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=True)
    created_at = Column(TIMESTAMP, default=func.now(), nullable=False)

    user = relationship("Usuario", back_populates="chat_conversations")
    messages = relationship("ChatMessage", back_populates="conversation")

# Modelo para a tabela 'chat_messages'
class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("chat_conversations.id", ondelete="CASCADE"), nullable=False)
    sender = Column(Enum("USER", "AI"), nullable=False)
    content = Column(Text, nullable=False)
    attachment_url = Column(String(1024), nullable=True)
    created_at = Column(TIMESTAMP, default=func.now(), nullable=False)

    conversation = relationship("ChatConversation", back_populates="messages")