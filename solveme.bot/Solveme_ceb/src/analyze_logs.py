import re
import os
from collections import Counter

def analyze_chat_log():
    """
    Analisa o arquivo de log do chat para identificar padrões.
    """
    # Pega o caminho do diretório onde este script está ('src')
    script_dir = os.path.dirname(__file__)
    # Monta o caminho para o arquivo de log na raiz do projeto
    log_file_path = os.path.abspath(os.path.join(script_dir, os.pardir, "logs", "chat_log.txt"))

    if not os.path.exists(log_file_path):
        print(f"Erro: Arquivo de log não encontrado em '{log_file_path}'.")
        print("Por favor, execute o bot primeiro para gerar o log.")
        return

    user_questions = []
    bot_responses = []
    errors_found = []

    print(f"--- Iniciando análise do log: '{log_file_path}' ---")
    with open(log_file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            match = re.search(r' - (.*)$', line)
            if not match:
                continue
            message_content = match.group(1)
            if message_content.startswith("Usuário:"):
                user_questions.append(message_content[len("Usuário:"):].strip())
            elif message_content.startswith("Bot:"):
                bot_responses.append(message_content[len("Bot:"):].strip())
            elif "Erro na execução:" in message_content:
                errors_found.append(f"Linha {line_num}: {message_content}")

    print("\n--- Resumo da Análise ---")
    print(f"Total de perguntas do usuário: {len(user_questions)}")
    print(f"Total de respostas do bot: {len(bot_responses)}")
    print(f"Total de erros registrados: {len(errors_found)}")
    if user_questions:
        print("\n--- Perguntas Mais Comuns (As 5 mais frequentes) ---")
        question_counts = Counter(user_questions)
        for question, count in question_counts.most_common(5):
            print(f"- '{question}' (ocorreu {count} vezes)")
    if errors_found:
        print("\n--- Detalhes dos Erros Encontrados ---")
        for error in errors_found:
            print(f"- {error}")
    print("\n--- Análise concluída ---")

if __name__ == "__main__":
    analyze_chat_log()