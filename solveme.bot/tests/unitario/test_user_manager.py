import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import time

# Importa a Base de database para criar tabelas SQLite em teste
from backend.database import Base 

# Importa os modelos, schemas e crud do pacote backend
from backend import models, schemas, crud 

# Importa as funções do user_manager e auth_utils
from backend.src import user_manager
# from backend.src import auth_utils # Não precisamos importar diretamente aqui, pois user_manager os usa

# Nome do arquivo de banco de dados SQLite para o teste
TEST_DATABASE_FILE = "sqlite:///./test_user_manager.db"

@pytest.fixture(scope="module")
def db_session_for_unit_test():
    """
    Fixture que configura um banco de dados SQLite temporário para os testes unitários
    do user_manager. Ela garante que a sessão do DB esteja disponível e limpa para cada módulo de teste.
    """
    # Remove qualquer arquivo de banco de dados de teste anterior para garantir um estado limpo
    file_path = TEST_DATABASE_FILE.replace("sqlite:///", "")
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            print(f"\nRemovido arquivo de DB de teste anterior: {file_path}")
        except PermissionError as e:
            print(f"\nWARNING: Não foi possível remover o arquivo de DB de teste: {e}. Remova manualmente.")
        except Exception as e:
            print(f"\nERRO INESPERADO ao remover arquivo de DB de teste: {e}")

    test_engine = create_engine(TEST_DATABASE_FILE)
    Base.metadata.create_all(bind=test_engine) # Cria as tabelas

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    # Retorna uma sessão do DB para que os testes possam usá-la
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=test_engine) # Limpa as tabelas após os testes
        test_engine.dispose()

        if os.path.exists(file_path):
            try:
                time.sleep(0.1) # Pequena pausa para garantir que o arquivo não esteja em uso
                os.remove(file_path)
            except PermissionError as e:
                print(f"WARNING: Não foi possível remover o arquivo de DB de teste após a execução: {e}")
                print(f"Por favor, remova '{file_path}' manualmente se persistir.")
            except Exception as e:
                print(f"ERRO INESPERADO ao remover arquivo de DB de teste: {e}")


# --- Testes para user_manager.py ---

def test_create_new_user(db_session_for_unit_test: Session):
    """
    Testa a criação de um novo usuário através do user_manager.
    Verifica se o usuário é salvo no DB de teste e se a senha é hasheada.
    """
    db = db_session_for_unit_test
    user_data = schemas.UserCreate(
        nome="Teste Criar",
        email="criar@test.com",
        telefone="11911111111",
        setor="QA",
        password="SenhaTeste123"
    )
    
    new_user = user_manager.create_new_user(db, user_data)
    
    assert new_user.id is not None
    assert new_user.email == user_data.email
    assert user_manager.auth_utils.verify_password(user_data.password, new_user.senha_hash) # Verifica o hash
    
    # Verifica diretamente no DB para garantir persistência
    retrieved_user = crud.get_user_by_email(db, user_data.email)
    assert retrieved_user.email == user_data.email


def test_authenticate_user_success(db_session_for_unit_test: Session):
    """
    Testa a autenticação bem-sucedida de um usuário.
    """
    db = db_session_for_unit_test
    # Crie um usuário primeiro
    user_data = schemas.UserCreate(
        nome="Teste Auth",
        email="auth@test.com",
        telefone="11922222222",
        setor="Dev",
        password="AuthPassword456"
    )
    user_manager.create_new_user(db, user_data)
    
    authenticated_user = user_manager.authenticate_user(db, user_data.email, user_data.password)
    assert authenticated_user is not None
    assert authenticated_user.email == user_data.email

def test_authenticate_user_failure_wrong_password(db_session_for_unit_test: Session):
    """
    Testa a falha de autenticação com senha incorreta.
    """
    db = db_session_for_unit_test
    user_data = schemas.UserCreate(
        nome="Teste Falha",
        email="fail@test.com",
        telefone="11933333333",
        setor="Ops",
        password="FailPassword789"
    )
    user_manager.create_new_user(db, user_data)
    
    authenticated_user = user_manager.authenticate_user(db, user_data.email, "WrongPassword")
    assert authenticated_user is None


def test_get_all_users(db_session_for_unit_test: Session):
    """
    Testa a obtenção de todos os usuários.
    """
    db = db_session_for_unit_test
    # Limpa usuários existentes para controle do teste
    for user in user_manager.get_all_users(db):
        user_manager.delete_user_by_id(db, user.id)

    # Cria alguns usuários
    user_manager.create_new_user(db, schemas.UserCreate(nome="User1", email="user1@test.com", telefone="1", setor="A", password="1"))
    user_manager.create_new_user(db, schemas.UserCreate(nome="User2", email="user2@test.com", telefone="2", setor="B", password="2"))
    
    users = user_manager.get_all_users(db)
    assert len(users) >= 2 # Pode haver o usuário padrão do DB
    assert any(u.email == "user1@test.com" for u in users)
    assert any(u.email == "user2@test.com" for u in users)


def test_get_user_by_id(db_session_for_unit_test: Session):
    """
    Testa a obtenção de um usuário por ID.
    """
    db = db_session_for_unit_test
    user_data = schemas.UserCreate(
        nome="Teste ID",
        email="id@test.com",
        telefone="11944444444",
        setor="Sec",
        password="IDPassword000"
    )
    new_user = user_manager.create_new_user(db, user_data)
    
    retrieved_user = user_manager.get_user_by_id(db, new_user.id)
    assert retrieved_user is not None
    assert retrieved_user.email == user_data.email
    assert retrieved_user.id == new_user.id

def test_update_existing_user(db_session_for_unit_test: Session):
    """
    Testa a atualização de um usuário existente.
    """
    db = db_session_for_unit_test
    user_data = schemas.UserCreate(
        nome="Teste Update",
        email="update@test.com",
        telefone="11955555555",
        setor="Admin",
        password="UpdatePassword111"
    )
    new_user = user_manager.create_new_user(db, user_data)
    
    update_data = schemas.UserUpdate(telefone="11999999999", setor="Gerência", eh_admin=True)
    updated_user = user_manager.update_existing_user(db, new_user.id, update_data)
    
    assert updated_user is not None
    assert updated_user.telefone == "11999999999"
    assert updated_user.setor == "Gerência"
    assert updated_user.eh_admin is True

def test_change_user_password(db_session_for_unit_test: Session):
    """
    Testa a alteração de senha de um usuário.
    """
    db = db_session_for_unit_test
    user_data = schemas.UserCreate(
        nome="Teste Senha",
        email="senha@test.com",
        telefone="11966666666",
        setor="User",
        password="OldPassword123"
    )
    new_user = user_manager.create_new_user(db, user_data)
    
    changed_user = user_manager.change_user_password(db, new_user.id, "OldPassword123", "NewSecurePassword456")
    assert changed_user is not None
    assert user_manager.auth_utils.verify_password("NewSecurePassword456", changed_user.senha_hash) # Verifica a nova senha


def test_delete_user_by_id(db_session_for_unit_test: Session):
    """
    Testa a exclusão de um usuário.
    """
    db = db_session_for_unit_test
    user_data = schemas.UserCreate(
        nome="Teste Delete",
        email="delete@test.com",
        telefone="11977777777",
        setor="Guest",
        password="DeletePassword777"
    )
    new_user = user_manager.create_new_user(db, user_data)
    
    deleted = user_manager.delete_user_by_id(db, new_user.id)
    assert deleted is True
    
    retrieved_user = user_manager.get_user_by_id(db, new_user.id)
    assert retrieved_user is None