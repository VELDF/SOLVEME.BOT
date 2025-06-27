from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

TEMP_USER = {
    "email": "admin@admin.com",
    "password": "admin"
}

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if email == TEMP_USER["email"] and password == TEMP_USER["password"]:
        return jsonify({"token": "fake-jwt-token", "user": {"email": email}}), 200

    return jsonify({"error": "Credenciais inválidas"}), 401

if __name__ == '__main__':
    app.run(port=5000, debug=True)