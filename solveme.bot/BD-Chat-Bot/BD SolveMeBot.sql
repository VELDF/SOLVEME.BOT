-- Cria o esquema (banco de dados) se ele ainda não existir
CREATE SCHEMA IF NOT EXISTS DBLogin;

-- Usa o esquema DBLogin para todas as operações subsequentes
USE DBLogin;

-- Descarte de tabelas na ordem inversa de suas dependências para evitar erros
-- 'IF EXISTS' garante que o comando não falhe se a tabela já não existir
DROP TABLE IF EXISTS feedback_attachments;
DROP TABLE IF EXISTS chat_messages;
DROP TABLE IF EXISTS tokens_recuperacao;
DROP TABLE IF EXISTS logins;
DROP TABLE IF EXISTS notes;
DROP TABLE IF EXISTS feedbacks;
DROP TABLE IF EXISTS chat_conversations;
DROP TABLE IF EXISTS usuarios;


-- Tabela de Usuários: armazena as informações principais da conta.
-- Explicação:
-- - `id`: Chave primária auto-incrementável para identificar unicamente cada usuário.
-- - `nome`: Nome completo do usuário.
-- - `email`: Endereço de e-mail empresarial, deve ser único para cada usuário e não pode ser nulo.
-- - `telefone`: Número de telefone do usuário.
-- - `setor`: Setor ou departamento ao qual o usuário pertence.
-- - `senha_hash`: Armazena o hash da senha (nunca a senha em texto puro) para segurança.
-- - `eh_admin`: Booleano para indicar se o usuário tem privilégios de administrador (padrão: FALSO).
-- - `ativo`: Booleano para indicar se a conta do usuário está ativa no sistema (padrão: VERDADEIRO).
-- - `criado_em`: Timestamp que registra a data e hora de criação do registro do usuário.
CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(250) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    telefone VARCHAR(16) NOT NULL,
    setor VARCHAR (100) NOT NULL,
    senha_hash VARCHAR(255) NOT NULL,
    eh_admin BOOLEAN NOT NULL DEFAULT FALSE,
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    criado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Adição de índices para otimizar buscas comuns
CREATE INDEX idx_usuarios_nome ON usuarios (nome);
CREATE INDEX idx_usuarios_setor ON usuarios (setor);


-- Tabela de Tokens: gerencia os códigos de uso único para recuperação de senha.
-- Explicação:
-- - `id`: Chave primária auto-incrementável.
-- - `usuario_id`: Referência ao ID do usuário associado a este token.
-- - `codigo`: O código de recuperação gerado (ex: 6 dígitos).
-- - `expiracao`: Timestamp que define quando o token deixa de ser válido. Essencial para segurança.
-- - `usado`: Booleano para indicar se o token já foi utilizado (padrão: FALSO).
-- - `criado_em`: Timestamp que registra a data e hora de criação do token.
-- - `FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE`:
--   Se um usuário for deletado, todos os tokens de recuperação associados a ele também serão deletados.
CREATE TABLE tokens_recuperacao (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    codigo VARCHAR(6) NOT NULL,
    expiracao TIMESTAMP NOT NULL,
    usado BOOLEAN NOT NULL DEFAULT FALSE,
    criado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Adição de índices para otimizar buscas e limpezas
CREATE INDEX idx_tokens_codigo ON tokens_recuperacao (codigo);
CREATE INDEX idx_tokens_expiracao_usado ON tokens_recuperacao (expiracao, usado);


-- Tabela de Logins: registra cada tentativa de login (sucesso ou falha).
-- Explicação:
-- - `id`: Chave primária auto-incrementável.
-- - `usuario_id`: Referência ao ID do usuário que tentou o login.
-- - `data_login`: Timestamp que registra a data e hora do login (padrão: momento atual).
-- - `ip_address`: Endereço IP de onde a tentativa de login foi feita (pode ser nulo).
-- - `sucesso`: Booleano para indicar se o login foi bem-sucedido (VERDADEIRO) ou falho (FALSO).
-- - `FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE`:
--   Se um usuário for deletado, todo o seu histórico de logins também será deletado.
CREATE TABLE logins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    data_login TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45) NULL, -- Tamanho para IPv6
    sucesso BOOLEAN NOT NULL,

    FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Adição de índices para otimizar buscas e relatórios de login
CREATE INDEX idx_logins_usuario_id ON logins (usuario_id);
CREATE INDEX idx_logins_data_login ON logins (data_login);
CREATE INDEX idx_logins_sucesso ON logins (sucesso);


-- Inserção de um usuário administrador padrão para testes/inicialização.
-- ATENÇÃO: Em produção, 'hashsegura123' DEVE ser substituído pelo hash REAL da senha gerado por bcrypt.
INSERT INTO usuarios (nome, email, telefone, setor, senha_hash, eh_admin, ativo)
VALUES ('Administrador Sistema', 'admin@sistema.com', '(XX) 9XXXX-XXXX', 'TI', 'hashsegura123', TRUE, TRUE);


-- Tabela de Notas (Bloco de Notas): armazena notas pessoais dos usuários.
-- Explicação:
-- - `id`: Chave primária auto-incrementável.
-- - `user_id`: Referência ao ID do usuário proprietário da nota.
-- - `title`: Título da nota (pode ser nulo).
-- - `content`: Conteúdo da nota (pode ser nulo, tipo TEXT para conteúdo longo).
-- - `created_at`: Timestamp de criação da nota.
-- - `updated_at`: Timestamp da última atualização da nota, atualizado automaticamente.
-- - `FOREIGN KEY (user_id) REFERENCES usuarios(id) ON DELETE CASCADE`:
--   Se um usuário for deletado, todas as suas notas também serão deletadas.
CREATE TABLE notes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(255) NULL,
    content TEXT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES usuarios (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Adição de índice para otimizar a recuperação de notas por usuário
CREATE INDEX idx_notes_user_id ON notes (user_id);
CREATE INDEX idx_notes_updated_at ON notes (updated_at);


-- Tabela de Feedbacks: armazena feedbacks, sugestões ou problemas relatados pelos usuários.
-- Explicação:
-- - `id`: Chave primária auto-incrementável.
-- - `user_id`: Referência ao ID do usuário que enviou o feedback (pode ser nulo para feedbacks anônimos).
-- - `type`: Tipo do feedback (PROBLEMA, IDEIA, OUTRO) usando ENUM para valores predefinidos.
-- - `message`: Conteúdo detalhado do feedback.
-- - `status`: Status atual do feedback (ABERTO, EM_ANALISE, CONCLUIDO) usando ENUM.
-- - `created_at`: Timestamp de criação do feedback.
-- - `FOREIGN KEY (user_id) REFERENCES usuarios(id) ON DELETE SET NULL`:
--   Se um usuário for deletado, o `user_id` neste feedback será definido como NULO, mantendo o feedback.
CREATE TABLE feedbacks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NULL,
    type ENUM('PROBLEMA', 'IDEIA', 'OUTRO') NOT NULL,
    message TEXT NOT NULL,
    status ENUM('ABERTO', 'EM_ANALISE', 'CONCLUIDO') NOT NULL DEFAULT 'ABERTO',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES usuarios (id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Adição de índices para otimizar filtros e relatórios de feedback
CREATE INDEX idx_feedbacks_user_id ON feedbacks (user_id);
CREATE INDEX idx_feedbacks_type ON feedbacks (type);
CREATE INDEX idx_feedbacks_status ON feedbacks (status);
CREATE INDEX idx_feedbacks_created_at ON feedbacks (created_at);


-- Tabela de Anexos do Feedback: armazena detalhes sobre arquivos anexados a feedbacks.
-- Explicação:
-- - `id`: Chave primária auto-incrementável.
-- - `feedback_id`: Referência ao ID do feedback ao qual este anexo pertence.
-- - `file_url`: URL ou caminho para o arquivo anexado (ex: URL em um serviço de armazenamento de nuvem).
-- - `file_type`: Tipo do arquivo (ex: 'image/png', 'application/pdf').
-- - `created_at`: Timestamp de criação do registro do anexo.
-- - `FOREIGN KEY (feedback_id) REFERENCES feedbacks(id) ON DELETE CASCADE`:
--   Se um feedback for deletado, todos os seus anexos também serão deletados.
CREATE TABLE feedback_attachments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    feedback_id INT NOT NULL,
    file_url VARCHAR(1024) NOT NULL,
    file_type VARCHAR(100) NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (feedback_id) REFERENCES feedbacks (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Adição de índice para otimizar a recuperação de anexos por feedback
CREATE INDEX idx_feedback_attachments_feedback_id ON feedback_attachments (feedback_id);


--------------------------------------------------------------------------------------------
-- Tabela de Conversas do Chatbot: armazena as sessões de conversa do chatbot.
-- Explicação:
-- - `id`: Chave primária auto-incrementável.
-- - `user_id`: Referência ao ID do usuário que iniciou a conversa.
-- - `title`: Título da conversa (pode ser gerado automaticamente ou pelo usuário).
-- - `created_at`: Timestamp de criação da conversa.
-- - `FOREIGN KEY (user_id) REFERENCES usuarios(id) ON DELETE CASCADE`:
--   Se um usuário for deletado, todas as suas conversas do chatbot também serão deletadas.
CREATE TABLE chat_conversations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(255) NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES usuarios (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Adição de índice para otimizar a recuperação de conversas por usuário
CREATE INDEX idx_chat_conversations_user_id ON chat_conversations (user_id);
CREATE INDEX idx_chat_conversations_created_at ON chat_conversations (created_at);


-- Tabela de Mensagens do Chatbot: armazena as mensagens individuais dentro de uma conversa.
-- Explicação:
-- - `id`: Chave primária auto-incrementável.
-- - `conversation_id`: Referência ao ID da conversa à qual esta mensagem pertence.
-- - `sender`: Indica quem enviou a mensagem (USER ou AI) usando ENUM.
-- - `content`: O conteúdo da mensagem (tipo TEXT para mensagens longas).
-- - `attachment_url`: URL de um anexo opcional na mensagem.
-- - `created_at`: Timestamp de criação da mensagem.
-- - `FOREIGN KEY (conversation_id) REFERENCES chat_conversations(id) ON DELETE CASCADE`:
--   Se uma conversa for deletada, todas as suas mensagens também serão deletadas.
CREATE TABLE chat_messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    conversation_id INT NOT NULL,
    sender ENUM('USER', 'AI') NOT NULL,
    content TEXT NOT NULL,
    attachment_url VARCHAR(1024) NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (conversation_id) REFERENCES chat_conversations (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Adição de índice para otimizar a recuperação de mensagens por conversa
CREATE INDEX idx_chat_messages_conversation_id ON chat_messages (conversation_id);
CREATE INDEX idx_chat_messages_created_at ON chat_messages (created_at);


-------------------------------------------------------------------------
-- NOTAS PARA O BACKEND:
-------------------------------------------------------------------------

-- 1. Criptografia de Senhas:
--    É CRÍTICO que você use uma biblioteca de hashing de senhas forte como 'bcrypt'
--    (ou Argon2/scrypt) no seu backend para armazenar e verificar senhas.
--    Exemplo (Node.js): npm install bcrypt

-- 2. Lógica de Validação de Login do Administrador (Exemplo):
--    Esta é apenas uma representação em SQL. No seu backend, você fará:
--    a. Buscar o usuário pelo 'email'.
--    b. Usar a biblioteca de hashing (ex: bcrypt.compare) para comparar
--       a senha fornecida pelo usuário com o 'senha_hash' armazenado no DB.
--    c. Verificar 'eh_admin' e 'ativo' no objeto do usuário recuperado.

-- Exemplo conceitual de SELECT (não use diretamente com senha_hash em texto puro):
-- SELECT id, nome, email, eh_admin, ativo FROM usuarios
-- WHERE email = 'admin@sistema.com'
--   AND eh_admin = TRUE
--   AND ativo = TRUE;
-- (A comparação da senha_hash seria feita no código do seu backend após recuperar o registro.)
