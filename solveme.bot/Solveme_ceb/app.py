import os
from flask import Flask, request, jsonify, g
from flask_cors import CORS
import jwt
import datetime
from functools import wraps
from notas import notas_bp
from login import login_bp
from feedback import feedback_bp
from mural import mural_bp
from login_edit import auth_bp as login_edit_bp
from configuracoes import configuracoes_bp
from db import init_app, close_db
from historico import historico_bp
from menu_admin import menu_admin_bp
from dashboard import dashboard_bp
from deshboard_admin import dashboard_admin_bp
from mural_admin import mural_admin_bp
from usuarios_admin import usuarios_admin_bp   
from feadback_admin import feedback_admin_bp
import hashlib
from dotenv import load_dotenv
from logger import setup_logger
from rate_limit import rate_limit

# Carrega variáveis de ambiente
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuração do logger
logger = setup_logger(app)

# Configuração segura da chave secreta
SECRET_KEY = os.getenv('SECRET_KEY', 'Admin@1234')
app.config['SECRET_KEY'] = SECRET_KEY

# Configuração de salt para senhas
SALT = os.getenv('SALT', 'salt_padrao_superseguro')

def hash_password(password):
    """Gera um hash seguro da senha."""
    return hashlib.sha256((password + SALT).encode()).hexdigest()

init_app(app)
app.teardown_appcontext(close_db)


@app.before_request
def before_request():
    """Middleware para processar requisições antes de serem tratadas."""
    logger.info(f"Requisição recebida: {request.method} {request.path}")
    if 'Authorization' in request.headers:
        auth_header = request.headers['Authorization']
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]
            try:
                data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
                user = next((u for u in users_db if u['email'] == data['email']), None)
                if user:
                    g.user_id = user['id']
                    logger.info(f"Usuário autenticado: {user['email']}")
            except Exception as e:
                logger.error(f"Erro na autenticação: {str(e)}")

# Banco de dados de usuários (em produção, usar banco de dados real)
users_db = [
    {"id": 1, "name": "John Shatam", "email": "john@mail.com", "password": hash_password("senha123")},
    {"id": 2, "name": "Lucas Silva", "email": "lucas@mail.com", "password": hash_password("123456")},
    {"id": 3, "name": "Amanda Costa", "email": "amanda@mail.com", "password": hash_password("senhaamanda")},
    {"id": 4, "name": "Roberto Torres", "email": "roberto@mail.com", "password": hash_password("torres2023")},
    {"id": 5, "name": "Mariana Lima", "email": "mariana@mail.com", "password": hash_password("mari123")},
    {"id": 6, "name": "Carlos Souza", "email": "carlos@mail.com", "password": hash_password("carl123")},
    {"id": 7, "name": "Fernanda Rocha", "email": "fernanda@mail.com", "password": hash_password("ferrocha")},
    {"id": 8, "name": "Daniel Alves", "email": "daniel@mail.com", "password": hash_password("dan123")},
    {"id": 9, "name": "Bruna Mendes", "email": "bruna@mail.com", "password": hash_password("bruninha")},
    {"id": 10, "name": "Thiago Ramos", "email": "thiago@mail.com", "password": hash_password("tramos123")}
]

# Banco de dados de itens
items_db = [
    {"id": 1, "name": "Item 1", "description": "Descrição do Item 1"},
    {"id": 2, "name": "Item 2", "description": "Descrição do Item 2"}
]

# Registra os blueprints
app.register_blueprint(notas_bp, url_prefix='/api')
app.register_blueprint(login_bp, url_prefix='/api')
app.register_blueprint(feedback_bp, url_prefix='/api')
app.register_blueprint(mural_bp, url_prefix='/api')
app.register_blueprint(login_edit_bp, url_prefix='/api')
app.register_blueprint(configuracoes_bp, url_prefix='/api')
app.register_blueprint(historico_bp, url_prefix='/api')
app.register_blueprint(dashboard_bp, url_prefix='/api')
app.register_blueprint(menu_admin_bp, url_prefix='/api')
app.register_blueprint(mural_admin_bp, url_prefix='/api')
app.register_blueprint(dashboard_admin_bp, url_prefix='/api')
app.register_blueprint(usuarios_admin_bp, url_prefix='/api')
app.register_blueprint(feedback_admin_bp, url_prefix='/api')

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header[7:]
        if not token:
            logger.warning("Tentativa de acesso sem token")
            return jsonify({'message': 'Token está faltando!'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = next((u for u in users_db if u['email'] == data['email']), None)
            if not current_user:
                raise Exception("Usuário não encontrado")
        except Exception as e:
            logger.error(f"Erro na validação do token: {str(e)}")
            return jsonify({'message': 'Token inválido!'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

@app.route('/', methods=['GET'])
def home():
    """Rota raiz da aplicação."""
    logger.info("Acesso à rota raiz")
    return "Servidor Flask está rodando! Rota raiz funcionando."

@app.route('/register', methods=['POST'])
@rate_limit
def register():
    """Endpoint para registro de novos usuários."""
    data = request.json
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    if not name or not email or not password:
        logger.warning("Tentativa de registro com campos incompletos")
        return jsonify({"message": "Campos incompletos"}), 400

    if any(u['email'] == email for u in users_db):
        logger.warning(f"Tentativa de registro com email já existente: {email}")
        return jsonify({"message": "Usuário já cadastrado"}), 400

    users_db.append({
        "id": len(users_db) + 1,
        "name": name,
        "email": email,
        "password": hash_password(password)
    })
    logger.info(f"Novo usuário registrado: {email}")
    return jsonify({"message": "Usuário cadastrado com sucesso"}), 201

@app.route('/login', methods=['POST'])
@rate_limit
def login():
    """Endpoint para autenticação de usuários."""
    data = request.json
    email = data.get('email')
    password = data.get('password')

    user = next((u for u in users_db if u['email'] == email and u['password'] == hash_password(password)), None)
    if not user:
        logger.warning(f"Tentativa de login falha para o email: {email}")
        return jsonify({"message": "Email ou senha incorretos"}), 401

    token = jwt.encode({
        'email': user['email'],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=2)
    }, app.config['SECRET_KEY'], algorithm="HS256")

    logger.info(f"Login bem-sucedido para o usuário: {email}")
    return jsonify({"token": token})

@app.route('/profile', methods=['GET'])
@token_required
def profile(current_user):
    """Endpoint para obter informações do perfil do usuário."""
    logger.info(f"Acesso ao perfil do usuário: {current_user['email']}")
    return jsonify({
        "name": current_user['name'],
        "email": current_user['email']
    })

@app.route('/items', methods=['GET'])
@token_required
def get_items(current_user):
    return jsonify(items_db)

@app.route('/users', methods=['GET'])
@token_required
def get_users(current_user):
    users_sanitized = [{"id": u.get("id", idx + 1), "name": u["name"], "status": u.get("status", True), "onof": u.get("onof", False)} for idx, u in enumerate(users_db)]
    return jsonify(users_sanitized)

@app.route('/users/<int:id>', methods=['GET'])
@token_required
def get_user_by_id(current_user, id):
    user = next((u for u in users_db if u['id'] == id), None)
    if not user:
        return jsonify({"message": "Usuário não encontrado"}), 404

    return jsonify({
        "id": user["id"],
        "name": user["name"],
        "email": user["email"],
        "telefone": user.get("telefone", ""),
        "setor": user.get("setor", ""),
        "status": user.get("status", True),
        "onof": user.get("onof", False)
    })

@app.errorhandler(404)
def not_found(error):
    """Handler para rotas não encontradas."""
    logger.warning(f"Rota não encontrada: {request.path}")
    return jsonify({"message": "Rota não encontrada"}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handler para erros internos do servidor."""
    logger.error(f"Erro interno do servidor: {str(error)}")
    return jsonify({"message": "Erro interno do servidor"}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(debug=os.getenv('FLASK_DEBUG', '1') == '1', port=port)
