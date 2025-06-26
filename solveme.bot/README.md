# Backend Flask para app Angular

## Como rodar

1. Crie um ambiente virtual (opcional, recomendado):
```
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate   # Windows
```

2. Instale as dependências:
```
pip install -r requirements.txt
```

3. Execute o servidor:
```
python app.py
```

## Rotas disponíveis

- POST /register
- POST /login
- GET /profile (requere token JWT no header Authorization)
- GET /items (requere token JWT)

Use o token retornado no login para acessar rotas protegidas com o header:

```
Authorization: Bearer <token>
```

---