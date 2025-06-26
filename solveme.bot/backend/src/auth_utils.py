from passlib.context import CryptContext

# Certifique-se de ter instalado: pip install "passlib[bcrypt]"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Função que retorna o hash da senha
def get_password_hash(password: str) -> str:
    """Gera o hash de uma senha usando bcrypt."""
    return pwd_context.hash(password)

# Função que verifica a senha
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se uma senha em texto puro corresponde a um hash."""
    return pwd_context.verify(plain_password, hashed_password)