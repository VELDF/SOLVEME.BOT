# solve_me_bot/tests/e2e/test_users_e2e_flow.py
import pytest
import os
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, clear_mappers
from backend.database import Base, get_db as original_get_db, create_db_engine
from backend.main import app # Importa a aplicação FastAPI do backend de usuários
from fastapi.testclient import TestClient # Usado para simular requisições HTTP

@pytest.fixture(scope="module")
def client():
    # Cria um engine SQLite em memória para os testes de API deste módulo
    engine = create_db_engine("sqlite:///./test_e2e_users.db")
    
    Base.metadata.create_all(bind=engine) # Cria as tabelas no DB em memória antes de todos os testes do módulo
    
    # Sobrescreve a dependência de DB da aplicação FastAPI para usar nosso DB de teste
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[original_get_db] = override_get_db

    try:
        with TestClient(app=app, base_url="http://test") as test_client_instance:
            yield test_client_instance
    finally:
        # Limpeza após todos os testes do módulo
        app.dependency_overrides.clear() # Limpa as sobrescritas de dependência
        Base.metadata.drop_all(bind=engine)
        clear_mappers()
        engine.dispose()
        
        if os.path.exists("./test_e2e_users.db"):
            try:
                time.sleep(0.1)
                os.remove("./test_e2e_users.db")
            except PermissionError as e:
                print(f"\nWARNING: Não foi possível remover o arquivo de DB de teste E2E: {e}")
            except Exception as e:
                print(f"\nERRO INESPERADO ao remover arquivo de DB de teste E2E: {e}")

def test_full_user_management_flow(client: TestClient):
    """
    Simula o fluxo completo de gerenciamento de um usuário:
    Criação -> Listagem -> Leitura (Perfil) -> Edição -> Ativação/Desativação -> Alteração de Senha -> Deleção.
    """
    user_id = None # Para armazenar o ID do usuário criado

    # 1. Criar um novo usuário (Simula o 'Adicionar usuário' da tela de Gerenciamento)
    print("\n--- Teste E2E: Criando usuário ---")
    create_response = client.post(
        "/users/",
        json={
            "email": "e2e_user@example.com",
            "password": "E2ePassword123",
            "name": "E2E Test User",
            "role": "Software Tester",
            "phone": "551199887766"
        }
    )
    assert create_response.status_code == 201
    created_user_data = create_response.json()
    user_id = created_user_data["id"]
    assert created_user_data["email"] == "e2e_user@example.com"
    assert created_user_data["name"] == "E2E Test User"
    assert "id" in created_user_data
    assert created_user_data["is_active"] is True
    print(f"Usuário criado com ID: {user_id}")

    # 2. Listar usuários (Simula a tela de 'Gerenciamento de Usuários')
    print("\n--- Teste E2E: Listando usuários ---")
    list_response = client.get("/users/")
    assert list_response.status_code == 200
    listed_users = list_response.json()
    assert isinstance(listed_users, list)
    assert len(listed_users) >= 1
    assert any(user["id"] == user_id for user in listed_users)
    print(f"Usuário ID {user_id} encontrado na lista.")

    # 3. Ler detalhes do usuário (Simula a abertura da tela de 'Perfil do Usuário')
    print("\n--- Teste E2E: Lendo detalhes do perfil ---")
    read_response = client.get(f"/users/{user_id}")
    assert read_response.status_code == 200
    read_user_data = read_response.json()
    assert read_user_data["id"] == user_id
    assert read_user_data["email"] == "e2e_user@example.com"
    assert read_user_data["name"] == "E2E Test User"
    print(f"Detalhes do usuário ID {user_id} lidos com sucesso.")

    # 4. Editar o usuário (Simula a atualização de Telefone/Cargo na tela de 'Perfil')
    print("\n--- Teste E2E: Editando perfil (telefone e cargo) ---")
    update_response = client.put(
        f"/users/{user_id}",
        json={"phone": "5511911223344", "role": "Senior Software Tester"}
    )
    assert update_response.status_code == 200
    updated_user_data = update_response.json()
    assert updated_user_data["phone"] == "5511911223344"
    assert updated_user_data["role"] == "Senior Software Tester"
    assert updated_user_data["email"] == "e2e_user@example.com"
    print(f"Perfil do usuário ID {user_id} atualizado com sucesso.")

    # 5. Ativar/Desativar usuário (Simula o switch na tela de 'Gerenciamento')
    print("\n--- Teste E2E: Desativando usuário ---")
    deactivate_response = client.put(
        f"/users/{user_id}",
        json={"is_active": False}
    )
    assert deactivate_response.status_code == 200
    assert deactivate_response.json()["is_active"] is False
    print(f"Usuário ID {user_id} desativado.")

    print("\n--- Teste E2E: Ativando usuário ---")
    activate_response = client.put(
        f"/users/{user_id}",
        json={"is_active": True}
    )
    assert activate_response.status_code == 200
    assert activate_response.json()["is_active"] is True
    print(f"Usuário ID {user_id} ativado.")

    # 6. Alterar senha do usuário (Simula o botão 'Alterar Senha' na tela de 'Perfil')
    print("\n--- Teste E2E: Alterando senha ---")
    change_password_response = client.post(
        f"/users/{user_id}/change-password",
        json={"old_password": "E2ePassword123", "new_password": "NewE2ePass!@#"}
    )
    assert change_password_response.status_code == 200
    assert change_password_response.json()["message"] == "Senha alterada com sucesso"
    print(f"Senha do usuário ID {user_id} alterada com sucesso.")

    # 7. Tentar alterar senha com senha antiga incorreta
    print("\n--- Teste E2E: Tentando alterar senha com senha antiga incorreta (deve falhar) ---")
    change_password_fail_response = client.post(
        f"/users/{user_id}/change-password",
        json={"old_password": "WrongPassword", "new_password": "ShouldNotChange"}
    )
    assert change_password_fail_response.status_code == 400
    print(f"Tentativa de alteração de senha falhou como esperado (cód. {change_password_fail_response.status_code}).")


    # 8. Deletar o usuário (Simula uma ação de exclusão da tela de 'Gerenciamento')
    print("\n--- Teste E2E: Deletando usuário ---")
    delete_response = client.delete(f"/users/{user_id}")
    assert delete_response.status_code == 204
    print(f"Usuário ID {user_id} deletado com sucesso.")

    # 9. Verificar que o usuário foi deletado (Não deve mais aparecer na listagem ou busca por ID)
    print("\n--- Teste E2E: Verificando deleção ---")
    get_deleted_response = client.get(f"/users/{user_id}")
    assert get_deleted_response.status_code == 404
    assert get_deleted_response.json()["detail"] == "Usuário não encontrado"
    print(f"Verificado: Usuário ID {user_id} não é mais encontrado (cód. {get_deleted_response.status_code}).")

    print("\n--- Fluxo E2E de Gerenciamento de Usuário CONCLUÍDO COM SUCESSO! ---")