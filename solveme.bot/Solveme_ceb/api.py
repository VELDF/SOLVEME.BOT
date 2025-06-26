import os
import logging
import json
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session # Importado para a injeção de dependência do DB
from dotenv import load_dotenv

# ADICIONADO: Importações necessárias para hints de tipo
from typing import AsyncGenerator, List, Dict 

# ADICIONADO: Importa o cliente Groq. Certifique-se que 'groq' está no seu requirements.txt
from groq import Groq

# IMPORTAÇÕES ATUALIZADAS: Módulos do seu backend, agora com o caminho completo para o pacote 'backend'
# Assumimos que a pasta 'backend' está na raiz do seu projeto (SOLVEME.BOT/)
from backend.database import engine, Base, get_db
from backend import models, schemas, crud # Importa models, schemas e crud como parte do pacote 'backend'

# Importa as funcionalidades do seu bot (caminhos internos a Solveme_ceb/src/ permanecem os mesmos)
from src.main import find_local_knowledge, search_web_for_knowledge, conversational_response
# A ferramenta check_printer_status é importada dinamicamente onde usada, para evitar importações cíclicas se src.tools
# também dependesse de módulos do backend de alguma forma.

# Carrega variáveis de ambiente do arquivo .env (assumindo que está na raiz do projeto ou no Solveme_ceb)
load_dotenv()

# Inicializa o cliente Groq com sua API Key
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    raise ValueError("GROQ_API_KEY não configurada no arquivo .env")
groq_client = Groq(api_key=groq_api_key)

# Configurações do logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# Garante que a pasta 'logs' exista dentro de Solveme_ceb/
if not os.path.exists("logs"):
    os.makedirs("logs")
file_handler = logging.FileHandler("logs/chat_log.txt") # Mantém o log em arquivo por enquanto para depuração
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logging.getLogger().addHandler(file_handler)

app = FastAPI()

# Configuração CORS para permitir requisições do seu frontend
app.add_middleware(
    CORSMiddleware,
    # ATENÇÃO: Em produção, substitua "*" pelo(s) domínio(s) exato(s) do seu frontend!
    # Exemplo para desenvolvimento local: allow_origins=["http://localhost:5500", "http://127.0.0.1:5500"]
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Evento de inicialização da aplicação: Cria as tabelas no banco de dados se não existirem
@app.on_event("startup")
def startup_event():
    # Base está sendo importada do módulo 'backend.database'
    Base.metadata.create_all(bind=engine)
    logging.info("Tabelas do banco de dados criadas/verificadas com sucesso.")

# Endpoint de teste para verificar o status do servidor
@app.get("/")
async def read_root():
    return {"message": "Solveme.Bot Backend is running!"}

# Função auxiliar para transmitir mensagens de status no formato JSON
async def stream_status_message(message: str) -> AsyncGenerator[str, None]:
    # Envia um objeto JSON para o frontend, que pode parsear e exibir como status
    yield f"data: {json.dumps({'type': 'status', 'content': message})}\n\n"

# Endpoint principal para processar a pergunta do bot
@app.post("/ask", response_class=StreamingResponse)
async def ask_bot(request: schemas.ChatRequest, db: Session = Depends(get_db)):
    prompt = request.prompt
    # O history do request pode ser usado para dar contexto inicial ao LLM,
    # mas o histórico completo será buscado do DB.
    
    # --- Lógica de Criação/Recuperação da Conversa e Usuário (NOVO) ---
    # PARA TESTE: Usamos um user_id fixo = 1. Em produção, este ID viria da autenticação do usuário.
    # A lógica atual cria uma NOVA conversa a cada requisição /ask. Para continuar uma conversa
    # existente, o frontend precisaria enviar um conversation_id.
    fixed_user_id = 1 
    
    # Verifica se o usuário placeholder com ID 1 existe, se não, tenta criá-lo
    # Isso é apenas para facilitar o teste inicial sem um sistema de registro/login completo.
    user_exists = db.query(models.Usuario).filter(models.Usuario.id == fixed_user_id).first()
    if not user_exists:
        try:
            # Atenção: 'senha_hasheada_inicial' é um placeholder. Use bcrypt em produção!
            placeholder_user = schemas.UserCreate(
                nome="Usuario Teste",
                email="teste@sistema.com",
                telefone="11999999999",
                setor="Geral",
                password="senha_segura_hash" 
            )
            crud.create_user(db, placeholder_user, "senha_hasheada_inicial") # Salva um hash simples por enquanto
            logging.warning(f"Usuário placeholder com ID {fixed_user_id} e email 'teste@sistema.com' criado para teste.")
        except Exception as e:
            # Captura exceções como email duplicado (se o usuário já foi criado por outro processo)
            logging.error(f"Erro ao criar usuário placeholder: {e}")
            # Se o erro for por email duplicado e o usuário já existir, podemos ignorar e continuar
            if "Duplicate entry" not in str(e): # Exemplo de verificação simples para erro de duplicidade
                raise HTTPException(status_code=500, detail="Erro interno ao preparar o usuário.")

    # Cria uma nova conversa para esta interação no DB
    # O título é limitado aos primeiros 50 caracteres do prompt
    conversation = crud.create_chat_conversation(db, user_id=fixed_user_id, title=prompt[:50])
    conversation_id = conversation.id
    logging.info(f"Nova conversa criada (ID: {conversation_id}) para o usuário {fixed_user_id}.")

    # Salva a mensagem do usuário no banco de dados
    crud.create_chat_message(db, conversation_id, "USER", prompt)
    logging.info(f"Usuário ({fixed_user_id}) - Pergunta: {prompt}")

    # Recupera o histórico COMPLETO da conversa do banco de dados para enviar ao LLM
    db_messages = crud.get_chat_messages(db, conversation_id)
    # Formata as mensagens do DB para o formato que o LLM espera ([{"role": "user", "content": "..."}, ...])
    llm_history = [{"role": msg.sender.lower(), "content": msg.content} for msg in db_messages if msg.sender in ["USER", "AI"]]

    # Define a função assíncrona que gerará o stream de resposta
    async def get_bot_response_stream(prompt_text: str, current_llm_history: List[Dict[str, str]]) -> AsyncGenerator[str, None]:
        # Tenta uma resposta conversacional simples primeiro (para "olá", "bom dia", etc.)
        simple_response = conversational_response(prompt_text)
        if simple_response:
            yield await stream_status_message("Resposta simples...")
            full_response_content = simple_response
            logging.info(f"Bot - Resposta Simples: {full_response_content}")
        else:
            # Se não houver resposta simples, procede com a busca de conhecimento e LLM
            local_search_result = find_local_knowledge(prompt_text)
            final_context_for_llm = ""
            
            # Prioriza a base de conhecimento local
            if local_search_result and local_search_result.get('content'):
                final_context_for_llm += local_search_result['content']
                yield await stream_status_message("Informações encontradas na base de conhecimento local.")
                
                # Se a relevância local for baixa, complementa com busca web
                if local_search_result.get('relevance_level') in ["low", "none"]:
                    web_search_result = search_web_for_knowledge(prompt_text)
                    if web_search_result:
                        final_context_for_llm += "\n\nInformações adicionais da web:\n" + web_search_result
                        yield await stream_status_message("Buscando na web para complementar...")
            else:
                # Se nada for encontrado localmente, busca diretamente na web
                web_search_result = search_web_for_knowledge(prompt_text)
                if web_search_result:
                    final_context_for_llm += web_search_result
                    yield await stream_status_message("Buscando informações na web...")
                else:
                    # Se nenhuma informação relevante for encontrada (local ou web)
                    yield await stream_status_message("Desculpe, não consegui encontrar informações relevantes nas minhas fontes.")

            # Prepara o prompt do sistema para o LLM
            system_prompt = (
                "Você é um assistente técnico inteligente focado em TI, impressoras Lexmark, VPN, MFA e mapeamento de pastas. "
                "Sempre responda em PORTUGUÊS do Brasil. "
                "Priorize informações do contexto fornecido, que pode vir de uma base de conhecimento local e/ou da web. "
                "Se o contexto for insuficiente, use seu conhecimento geral para fornecer uma resposta útil. "
                "Formate suas respostas usando Markdown para listas, passos e blocos de código quando apropriado. "
                "Se o usuário pedir algo sobre o status de uma impressora e fornecer um IP, use a ferramenta `check_printer_status` com o IP. "
                "Contexto de conhecimento:\n" + final_context_for_llm if final_context_for_llm else ""
            )

            # Prepara a lista de mensagens para o LLM (inclui sistema, histórico e prompt atual)
            messages = [
                {"role": "system", "content": system_prompt}
            ]
            messages.extend(current_llm_history) # Adiciona o histórico completo do DB
            messages.append({"role": "user", "content": prompt_text}) # Adiciona a pergunta atual

            full_response_content = ""
            try:
                # Chama a API da Groq para obter a resposta do LLM
                chat_completion = await groq_client.chat.completions.create(
                    messages=messages,
                    model="llama3-70b-8192", # Modelo LLM a ser usado
                    stream=True, # Habilita streaming da resposta
                    tools=[ # Definição das ferramentas que o LLM pode usar
                        {
                            "type": "function",
                            "function": {
                                "name": "check_printer_status",
                                "description": "Verifica o status de uma impressora dado um endereço IP. Retorna se a impressora está online ou offline.",
                                "parameters": {
                                    "type": "object",
                                    "properties": {
                                        "ip_address": {"type": "string", "description": "O endereço IP da impressora."}
                                    },
                                    "required": ["ip_address"],
                                },
                            }
                        }
                    ],
                )

                tool_call_performed = False # Flag para saber se uma ferramenta foi chamada

                # Itera sobre os chunks da resposta do LLM (streaming)
                async for chunk in chat_completion:
                    if chunk.choices[0].delta.content:
                        # Se for um pedaço da resposta de texto normal do LLM
                        full_response_content += chunk.choices[0].delta.content
                        yield f"data: {json.dumps({'type': 'text', 'content': chunk.choices[0].delta.content})}\n\n"
                    elif chunk.choices[0].delta.tool_calls:
                        # Se o LLM decidir chamar uma ferramenta
                        tool_call = chunk.choices[0].delta.tool_calls[0]
                        function_name = tool_call.function.name
                        function_args = json.loads(tool_call.function.arguments)

                        if function_name == "check_printer_status":
                            # Importa a ferramenta dinamicamente para evitar dependências circulares
                            from src.tools import check_printer_status
                            yield await stream_status_message(f"Executando ferramenta: {function_name} com IP {function_args.get('ip_address')}...")
                            tool_output = check_printer_status(ip_address=function_args.get("ip_address"))
                            
                            # Adiciona o resultado da ferramenta ao histórico de mensagens para o LLM
                            # e faz uma nova chamada ao LLM para interpretar o resultado
                            messages.append(
                                {
                                    "role": "tool",
                                    "tool_call_id": tool_call.id, # É importante incluir o tool_call_id para o LLM
                                    "name": function_name,
                                    "content": tool_output,
                                }
                            )
                            # Segunda chamada ao LLM para obter a resposta final após a execução da ferramenta
                            follow_up_completion = await groq_client.chat.completions.create(
                                messages=messages,
                                model="llama3-70b-8192",
                                stream=True,
                            )
                            async for follow_up_chunk in follow_up_completion:
                                if follow_up_chunk.choices[0].delta.content:
                                    full_response_content += follow_up_chunk.choices[0].delta.content
                                    yield f"data: {json.dumps({'type': 'text', 'content': follow_up_chunk.choices[0].delta.content})}\n\n"
                            tool_call_performed = True
                            break # Sai do loop principal após a chamada da ferramenta e follow-up
                
                # Se nenhuma ferramenta foi chamada e a resposta ainda está vazia
                if not tool_call_performed and not full_response_content.strip():
                    full_response_content = "Não consegui gerar uma resposta detalhada no momento."
                    yield f"data: {json.dumps({'type': 'text', 'content': full_response_content})}\n\n"

            except Exception as e:
                logging.error(f"Erro ao chamar o LLM ou processar stream: {e}")
                full_response_content = "Desculpe, tive um problema ao processar sua solicitação. Por favor, tente novamente."
                yield f"data: {json.dumps({'type': 'text', 'content': full_response_content})}\n\n"
        
        # Salva a resposta COMPLETA do bot no banco de dados após o término do stream
        crud.create_chat_message(db, conversation_id, "AI", full_response_content)
        logging.info(f"Bot - Resposta: {full_response_content}")

        # Envia um marcador de fim de stream para o frontend
        yield "data: [DONE]\n\n"

    # Retorna a StreamingResponse com a função geradora
    return StreamingResponse(get_bot_response_stream(prompt, llm_history), media_type="text/event-stream")
