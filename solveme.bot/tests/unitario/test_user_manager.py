# solveme_bot/tests/unitario/test_user_manager.py
import pytest
from sqlalchemy import create_engine, select # Adicionado select para SQLAlchemy 2.0
from sqlalchemy.orm import sessionmaker, clear_mappers, Session # Importar Session
from backend.database import Base # Importa a Base do seu database.py centralizado
from backend.models import User # Importa o modelo User
from backend.schemas import UserCreate, UserUpdate, UserChangePassword # Schemas Pydantic
from backend.src import user_manager, auth_utils
from typing import List, Optional # Importado Optional e List para type hints

# Fixture para criar um banco de dados SQLite em memória para cada teste unitário
@pytest.fixture(scope="function")
def db_session():
    engine = create_engine("sqlite:///:memory:") # DB SQLite em memória
    Base.metadata.create_all(bind=engine) # Cria as tabelas para o teste
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    try:
        yield db # Fornece a sessão para o teste
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine) # Limpa as tabelas após o teste
        clear_mappers() # Limpa os mappers do SQLAlchemy para evitar redefinição

def test_create_user(db_session: Session):
    """Verifica se um usuário pode ser criado corretamente."""
    email = "test@example.com"
    password = "secure_password"
    hashed_password = auth_utils.get_password_hash(password)
    user_data = UserCreate(email=email, password=password, name="Teste", role="Dev", phone="123456789")
    
    user = user_manager.create_user(db_session, user=user_data, hashed_password=hashed_password)
    
    assert user.email == email
    assert user.name == "Teste"
    assert user.is_active is True
    assert user.id is not None
    assert db_session.query(User).count() == 1 # Confirma que 1 usuário foi adicionado

def test_get_user(db_session: Session):
    """Verifica se um usuário pode ser recuperado pelo ID."""
    email = "get@example.com"
    password = "password"
    hashed_password = auth_utils.get_password_hash(password)
    user_data = UserCreate(email=email, password=password, name="Getter", role="QA")
    created_user = user_manager.create_user(db_session, user=user_data, hashed_password=hashed_password)

    retrieved_user = user_manager.get_user(db_session, user_id=created_user.id)
    assert retrieved_user is not None
    assert retrieved_user.email == email

def test_get_user_by_email(db_session: Session):
    """Verifica se um usuário pode ser recuperado pelo email."""
    email = "email@example.com"
    password = "password"
    hashed_password = auth_utils.get_password_hash(password)
    user_data = UserCreate(email=email, password=password)
    created_user = user_manager.create_user(db_session, user=user_data, hashed_password=hashed_password)

    retrieved_user = user_manager.get_user_by_email(db_session, email=email)
    assert retrieved_user is not None
    assert retrieved_user.id == created_user.id

def test_update_user(db_session: Session):
    """Verifica se os dados de um usuário podem ser atualizados."""
    email = "update@example.com"
    password = "password"
    hashed_password = auth_utils.get_password_hash(password)
    user_data = UserCreate(email=email, password=password, name="Old Name")
    created_user = user_manager.create_user(db_session, user=user_data, hashed_password=hashed_password)

    update_data = UserUpdate(name="New Name", phone="987654321")
    updated_user = user_manager.update_user(db_session, created_user.id, update_data)

    assert updated_user.name == "New Name"
    assert updated_user.phone == "987654321"
    assert updated_user.email == email # Email não mudou
    assert updated_user.id == created_user.id

def test_delete_user(db_session: Session):
    """Verifica se um usuário pode ser deletado."""
    email = "delete@example.com"
    password = "password"
    hashed_password = auth_utils.get_password_hash(password)
    user_data = UserCreate(email=email, password=password)
    created_user = user_manager.create_user(db_session, user=user_data, hashed_password=hashed_password)

    success = user_manager.delete_user(db_session, created_user.id)
    assert success is True
    assert user_manager.get_user(db_session, created_user.id) is None # Usuário deve ter sumido

def test_change_user_password(db_session: Session):
    """Verifica a funcionalidade de alteração de senha."""
    email = "password@example.com"
    old_password = "OldSecurePassword"
    new_password = "NewSecurePassword"
    hashed_old_password = auth_utils.get_password_hash(old_password)
    user_data = UserCreate(email=email, password=old_password)
    created_user = user_manager.create_user(db_session, user=user_data, hashed_password=hashed_old_password)

    # Tentar mudar a senha
    success = user_manager.change_user_password(db_session, created_user.id, old_password, new_password)
    assert success is True
    
    # Verificar se a nova senha funciona
    updated_user = user_manager.get_user(db_session, created_user.id)
    assert auth_utils.verify_password(new_password, updated_user.hashed_password) is True
    assert not auth_utils.verify_password(old_password, updated_user.hashed_password) # Antiga não deve funcionar

def test_change_user_password_incorrect_old_password(db_session: Session):
    """Verifica se a alteração de senha falha com senha antiga incorreta."""
    email = "failpassword@example.com"
    old_password = "CorrectOldPassword"
    new_password = "NewSecurePassword"
    hashed_old_password = auth_utils.get_password_hash(old_password)
    user_data = UserCreate(email=email, password=old_password)
    created_user = user_manager.create_user(db_session, user=user_data, hashed_password=hashed_old_password)

    success = user_manager.change_user_password(db_session, created_user.id, "WrongOldPassword", new_password)
    assert success is False
    
    # Garante que a senha não foi alterada
    updated_user = user_manager.get_user(db_session, created_user.id)
    assert auth_utils.verify_password(old_password, updated_user.hashed_password) is True