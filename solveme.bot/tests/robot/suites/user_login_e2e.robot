***Settings***
Documentation    Este teste simula o fluxo de login de um usuário na interface do Solveme.Bot.
Resource         ../resources/common_keywords.robot

***Test Cases***
Successful User Login And Dashboard Navigation
    Open Browser To Frontend    ${FRONTEND_URL}/login
    User Login    admin@example.com    adminpassword    # <--- USE CREDENCIAIS VÁLIDAS DO SEU DB
    SeleniumLibrary.Close All Browsers 