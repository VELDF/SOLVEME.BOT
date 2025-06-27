# solveme.bot/backend_login/src/config.py

import os
from dotenv import load_dotenv

load_dotenv() # Carrega variáveis de ambiente do .env

SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-and-very-long-jwt-secret-key-please-change-this-for-login")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 # Tempo de expiração do token em minutos