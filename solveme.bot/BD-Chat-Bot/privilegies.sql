-- Certifique-se que o usuário já foi criado. Se não, crie primeiro:
-- CREATE USER 'solveme_user'@'%' IDENTIFIED BY 'sua_nova_senha';

GRANT ALL PRIVILEGES ON DBLogin.* TO 'solveme_user'@'%';
FLUSH PRIVILEGES;

ALTER USER 'root'@'localhost' IDENTIFIED BY '12re34tyg7'; -- <<-- DIGITE A SENHA QUE VOCÊ QUER USAR NO .ENV
FLUSH PRIVILEGES;