# src/main.py
import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage, HumanMessage
# A importação abaixo está atualizada conforme as discussões anteriores
from langchain_google_community import GoogleSearchAPIWrapper
from langchain_community.tools import DuckDuckGoSearchRun # Mantido como fallback
from dotenv import load_dotenv
import logging

load_dotenv()

# Configuração da pesquisa web (Google Search API)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")

if not GOOGLE_API_KEY or not GOOGLE_CSE_ID:
    logging.warning("Variáveis de ambiente GOOGLE_API_KEY ou GOOGLE_CSE_ID não configuradas. A busca na web pode não funcionar.")
    search = DuckDuckGoSearchRun() # Fallback to DuckDuckGo if Google Search not configured
else:
    search = GoogleSearchAPIWrapper(google_api_key=GOOGLE_API_KEY, google_cse_id=GOOGLE_CSE_ID)

# Carregar o modelo de embeddings
embeddings = HuggingFaceEmbeddings(model_name='paraphrase-multilingual-mpnet-base-v2')

# Caminhos
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
faiss_index_path = os.path.join(project_root, "faiss_index")

# Carregar o índice FAISS
try:
    if not os.path.exists(faiss_index_path):
        raise FileNotFoundError(f"Índice FAISS não encontrado em: {faiss_index_path}. Execute 'criar_indice.py' primeiro.")
    vectorstore = FAISS.load_local(faiss_index_path, embeddings, allow_dangerous_deserialization=True)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 1})
    logging.info("Índice FAISS carregado com sucesso.")
except Exception as e:
    logging.error(f"Erro ao carregar o índice FAISS: {e}")
    vectorstore = None
    retriever = None

# --- Prompt do Sistema para o solve ---
SYSTEM_PROMPT_TEMPLATE = """
Você é o Solveme.Bot, um assistente técnico especializado em fornecer suporte e informações sobre impressoras, especialmente Lexmark, e problemas de TI comuns como VPN, MFA e mapeamento de pastas.
**Sempre responda em PORTUGUÊS do Brasil.**
Seu objetivo é ser útil, técnico e fornecer respostas claras, bem estruturadas e detalhadas.

Aqui está o contexto relevante que você pode usar para responder. **Priorize e utilize todas as informações da base de conhecimento local fornecidas.**
{context}

Use as informações da web para COMPLEMENTAR o que já foi encontrado na base de conhecimento local, tornando a resposta mais completa, robusta e atualizada, se necessário.
Se você não tiver informações suficientes para fornecer uma resposta útil e técnica, você deve indicar explicitamente que não sabe a resposta para aquela questão e pode sugerir que o usuário forneça mais detalhes ou tente uma pergunta diferente.
Mantenha suas respostas objetivas, focadas em soluções técnicas e, quando aplicável, apresente as informações em formato de passos, listas ou blocos de código para melhor clareza.
Se a pergunta for um cumprimento simples como "Bom dia", "Olá" ou "Oi", responda de forma amigável e educada, e então pergunte proativamente como pode ajudar o usuário.
"""

# --- Funções de Busca ---

def find_local_knowledge(query: str, low_relevance_threshold: float = 0.6, high_relevance_threshold: float = 0.3):
    """
    Busca conhecimento na base de dados local (FAISS).
    Retorna o conteúdo encontrado e um booleano indicando se a relevância é alta.
    low_relevance_threshold: score acima do qual consideramos que não há nada relevante.
    high_relevance_threshold: score abaixo do qual consideramos que há algo altamente relevante.
    """
    if vectorstore is None:
        logging.warning("Vectorstore não está carregada. Não é possível buscar conhecimento local.")
        return {"content": None, "relevance_level": "none"}

    docs_with_scores = vectorstore.similarity_search_with_score(query, k=5)
    
    found_docs_content = []
    current_relevance_level = "none" # none, low, high

    if not docs_with_scores:
        logging.info("Documento encontrado na base local.")
        return {"content": None, "relevance_level": "none"}

    for doc, score in docs_with_scores:
        # Se o score for menor que o limite de baixa relevância, significa que encontramos algo.
        if score < low_relevance_threshold:
            found_docs_content.append(doc.page_content)
            logging.info(f"Documento local encontrado (score={score:.4f}): {doc.page_content[:50]}...")
            
            # Determina o nível de relevância geral
            if score < high_relevance_threshold:
                # Se encontramos algo altamente relevante, setamos o nível para "high"
                current_relevance_level = "high"
            elif current_relevance_level != "high": # Se não for high, e ainda não é high, setamos para "low"
                current_relevance_level = "low"
        else:
            logging.info(f"Documento local descartado por ser muito distante: score={score:.4f}, content={doc.page_content[:50]}...")

    if found_docs_content:
        return {"content": "\n\n".join(found_docs_content), "relevance_level": current_relevance_level}
    
    return {"content": None, "relevance_level": "none"}


def search_web_for_knowledge(query: str):
    """
    Realiza uma busca na web, focada no site da Lexmark.
    """
    try:
        logging.info(f"Realizando busca web por: '{query}' no site da Lexmark.")
        web_query = f"{query} site:lexmark.com" # Mantém o foco na Lexmark
        web_results = search.run(web_query)
        return web_results
    except Exception as e:
        logging.error(f"Erro na busca web: {e}")
        return None

def conversational_response(prompt: str):
    """
    Gera uma resposta simples para perguntas conversacionais.
    """
    if any(greeting in prompt.lower() for greeting in ["bom dia", "boa tarde", "boa noite", "olá", "oi", "e aí", "tudo bem"]):
        return "Olá! Como posso ajudar você hoje?"
    return None