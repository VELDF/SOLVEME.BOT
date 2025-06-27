***Settings***
Documentation    Este teste simula o fluxo completo de CRUD de usuários na interface do Solveme.Bot.
Resource         ../resources/common_keywords.robot
Resource         ../resources/user_management_keywords.robot

***Test Cases***
Full User Management Workflow Via UI
    Open Browser To Frontend    ${FRONTEND_URL}/login
    User Login    admin@example.com    adminpassword    # <--- USE CREDENCIAIS VÁLIDAS DO SEU DB
    Navigate To User Management

    # 1. Adicionar um novo usuário
    Add New User Via UI    test_robot@example.com    RobotPass123    Robot User    Robot Tester    11987654321
    Verify User Exists In List    Robot User

    # 2. Editar o usuário recém-criado
    Edit User Via UI    Robot User    11999998888    Senior Robot Tester
    Verify User Exists In List    Robot User

    # 3. Deletar o usuário
    Delete User Via UI    Robot User

    SeleniumLibrary.Close All Browsers 