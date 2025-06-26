# SOLVEME.BOT/tests/api/test_api_ask.py

import pytest
import os
import time
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, clear_mappers
from fastapi.testclient import TestClient

# Importa a aplicação FastAPI do seu Solveme_ceb
# Assumimos que Solveme_ceb/api.py é onde sua aplicação FastAPI 'app' está definida
from Solveme_ceb.api import app
# Importa as configurações do banco de dados do seu pacote 'backend'
# Note que 'engine as original_engine' não é estritamente necessário aqui,
# mas é bom manter a consistência se houver outras dependências que o usem.
from backend.database import Base, get_db as original_get_db # Importa Base e a função get_db original
from backend import models, crud # Para verificar diretamente no DB de teste usando models e crud

# Usaremos um banco de dados SQLite em arquivo para os testes de API.
# Isso é preferível a um DB completamente em memória para alguns cenários
# onde a persistência entre diferentes chamadas à fixture possa ser útil (embora aqui resete).
TEST_DATABASE_FILE = "./test_api_chat.db"

@pytest.fixture(scope="module")
def db_session_for_test():
    """
    Fixture que configura um banco de dados SQLite temporário para os testes de API,
    sobrescrevendo a dependência de DB do FastAPI.
    """
    # Remove qualquer arquivo de banco de dados de teste anterior para garantir um estado limpo
    if os.path.exists(TEST_DATABASE_FILE):
        try:
            os.remove(TEST_DATABASE_FILE)
            print(f"\nRemovido arquivo de DB de teste anterior: {TEST_DATABASE_FILE}")
        except PermissionError as e:
            print(f"\nWARNING: Não foi possível remover o arquivo de DB de teste: {e}. Por favor, remova manualmente.")

    # Cria um engine SQLite para o arquivo temporário
    test_engine = create_engine(TEST_DATABASE_FILE)
    Base.metadata.create_all(bind=test_engine) # Cria as tabelas no DB de teste

    # Cria uma SessionLocal de teste
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    # Sobrescreve a dependência `get_db` do FastAPI para que ela use nosso DB de teste
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
            
    app.dependency_overrides[original_get_db] = override_get_db

    # Retorna uma sessão para que os próprios testes possam interagir com o DB de teste
    yield TestingSessionLocal() 

    # --- Limpeza após todos os testes do módulo ---
    app.dependency_overrides.clear() # Limpa as sobrescritas de dependência no FastAPI
    Base.metadata.drop_all(bind=test_engine) # Remove as tabelas do DB de teste
    clear_mappers() # Limpa os mapeamentos ORM (importante para evitar side effects entre módulos/test runs)
    test_engine.dispose() # Garante que o engine e as conexões sejam fechados

    # Tenta remover o arquivo do DB novamente
    if os.path.exists(TEST_DATABASE_FILE):
        try:
            time.sleep(0.1) # Pequena pausa para garantir que o arquivo não esteja em uso
            os.remove(TEST_DATABASE_FILE)
            print(f"Removido arquivo de DB de teste: {TEST_DATABASE_FILE}")
        except PermissionError as e:
            print(f"WARNING: Não foi possível remover o arquivo de DB de teste após a execução: {e}")
            print(f"Por favor, remova '{TEST_DATABASE_FILE}' manualmente se persistir.")
        except Exception as e:
            print(f"ERRO INESPERADO ao remover arquivo de DB de teste: {e}")

@pytest.fixture(scope="module")
def client(db_session_for_test): # Esta fixture garante que o DB de teste esteja configurado antes do TestClient
    """
    Fixture que retorna uma instância do TestClient do FastAPI para fazer requisições à API.
    """
    with TestClient(app) as test_client_instance:
        yield test_client_instance

# --- Testes de API para o Endpoint /ask ---

def test_ask_simple_greeting(client: TestClient, db_session_for_test: sessionmaker):
    """
    Testa se o endpoint /ask responde a uma saudação simples e se as mensagens
    (usuário e bot) são salvas corretamente no banco de dados de teste.
    """
    prompt = "Olá"
    response = client.post("/ask", json={"prompt": prompt, "history": []})

    assert response.status_code == 200
    
    full_response_content = ""
    # Coleta o streaming de resposta
    for chunk in response.iter_content():
        if chunk:
            try:
                # Cada chunk é uma linha de "data: {...}\n\n"
                decoded_chunk = chunk.decode("utf-8").strip()
                if decoded_chunk.startswith("data: "):
                    json_data = json.loads(decoded_chunk[len("data: "):])
                    if json_data.get("type") == "text":
                        full_response_content += json_data.get("content", "")
                    # Podemos ignorar 'status' messages para a verificação do conteúdo final do bot
            except json.JSONDecodeError:
                continue # Ignora chunks que não são JSON válidos ou o "data: [DONE]"

    assert "Olá" in full_response_content or "ajudar" in full_response_content or "posso" in full_response_content, \
        f"Resposta simples esperada não encontrada. Conteúdo: {full_response_content}"
    
    # --- Verificação de Persistência no DB de Teste ---
    # Abre uma nova sessão para verificar o estado do DB após a requisição API
    db = db_session_for_test # db_session_for_test é a TestingSessionLocal()
    
    # Assumimos que o user_id fixo no api.py para testes é 1.
    user_id_for_test = 1 
    
    # Busca a última conversa para este user_id (que foi criada por esta requisição)
    latest_conversation = db.query(models.ChatConversation).filter(models.ChatConversation.user_id == user_id_for_test).order_by(models.ChatConversation.created_at.desc()).first()
    
    assert latest_conversation is not None, "Nenhuma conversa encontrada no DB de teste para o usuário de teste"
    
    # Busca as mensagens da última conversa
    messages_in_db = crud.get_chat_messages(db, latest_conversation.id)
    
    # Verifica se as mensagens do usuário e do bot foram salvas
    user_message_found = any(msg.sender == "USER" and prompt in msg.content for msg in messages_in_db)
    bot_message_found = any(msg.sender == "AI" and 
                            ("Olá" in msg.content or "ajudar" in msg.content or "posso" in msg.content) 
                            for msg in messages_in_db)

    assert user_message_found, "Mensagem do usuário não encontrada no DB de teste"
    assert bot_message_found, "Resposta do bot não encontrada no DB de teste"


def test_ask_with_knowledge_base_query(client: TestClient, db_session_for_test: sessionmaker):
    """
    Testa se uma pergunta que deve acionar a base de conhecimento funciona e
    se as mensagens são salvas no DB de teste.
    """
    prompt = "Como configurar a impressora Lexmark?"
    response = client.post("/ask", json={"prompt": prompt, "history": []})

    assert response.status_code == 200
    
    full_response_content = ""
    for chunk in response.iter_content():
        if chunk:
            try:
                decoded_chunk = chunk.decode("utf-8").strip()
                if decoded_chunk.startswith("data: "):
                    json_data = json.loads(decoded_chunk[len("data: "):])
                    if json_data.get("type") == "text":
                        full_response_content += json_data.get("content", "")
            except json.JSONDecodeError:
                continue

    assert "impressora" in full_response_content.lower() or "lexmark" in full_response_content.lower(), \
        f"Resposta da KB esperada não encontrada. Conteúdo: {full_response_content}"
    
    # --- Verificação de Persistência no DB de Teste ---
    db = db_session_for_test
    user_id_for_test = 1
    latest_conversation = db.query(models.ChatConversation).filter(models.ChatConversation.user_id == user_id_for_test).order_by(models.ChatConversation.created_at.desc()).first()
    messages_in_db = crud.get_chat_messages(db, latest_conversation.id)

    user_message_found = any(msg.sender == "USER" and prompt in msg.content for msg in messages_in_db)
    bot_message_found = any(msg.sender == "AI" and 
                            ("impressora" in msg.content.lower() or "lexmark" in msg.content.lower()) 
                            for msg in messages_in_db)

    assert user_message_found, "Mensagem do usuário (KB) não encontrada no DB de teste"
    assert bot_message_found, "Resposta do bot (KB) não encontrada no DB de teste"


def test_ask_with_tool_call_query(client: TestClient, db_session_for_test: sessionmaker):
    """
    Testa se uma pergunta que deve acionar a tool 'check_printer_status' funciona e
    se as mensagens são salvas no DB de teste.
    """
    prompt = "Qual o status da impressora no IP 192.168.1.1?"
    response = client.post("/ask", json={"prompt": prompt, "history": []})

    assert response.status_code == 200
    
    full_response_content = ""
    status_message_found = False
    for chunk in response.iter_content():
        if chunk:
            try:
                decoded_chunk = chunk.decode("utf-8").strip()
                json_data = json.loads(decoded_chunk[len("data: "):])
                if json_data.get("type") == "text":
                    full_response_content += json_data.get("content", "")
                elif json_data.get("type") == "status":
                    if "Executando ferramenta: check_printer_status" in json_data.get("content", ""):
                        status_message_found = True
            except (json.JSONDecodeError, IndexError): # Trata o caso de "data: [DONE]" ou outras não-JSON
                continue
    
    assert status_message_found, "Mensagem de status de execução de ferramenta não encontrada no stream."
    assert ("online" in full_response_content.lower() or "offline" in full_response_content.lower() or "status" in full_response_content.lower()), \
        f"A resposta final do bot não indica status da impressora. Conteúdo: {full_response_content}"

    # --- Verificação de Persistência no DB de Teste ---
    db = db_session_for_test
    user_id_for_test = 1
    latest_conversation = db.query(models.ChatConversation).filter(models.ChatConversation.user_id == user_id_for_test).order_by(models.ChatConversation.created_at.desc()).first()
    messages_in_db = crud.get_chat_messages(db, latest_conversation.id)

    user_message_found = any(msg.sender == "USER" and prompt in msg.content for msg in messages_in_db)
    bot_message_found = any(msg.sender == "AI" and 
                            ("online" in msg.content.lower() or "offline" in msg.content.lower() or "status" in msg.content.lower()) 
                            for msg in messages_in_db)

    assert user_message_found, "Mensagem do usuário (tool call) não encontrada no DB de teste"
    assert bot_message_found, "Resposta do bot (tool call) não encontrada no DB de teste"