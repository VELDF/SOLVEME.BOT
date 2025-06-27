***Settings***
Library    SeleniumLibrary
# Library    RequestsLibrary

***Variables***
${BROWSER}           Chrome
${FRONTEND_URL}      http://localhost:4200
${BACKEND_USERS_API_URL}    http://localhost:8002

***Keywords***
Open Browser To Frontend
    [Arguments]    ${url}=${FRONTEND_URL}
    Open Browser    ${url}    ${BROWSER}
    Maximize Browser Window
    Set Selenium Implicit Wait    5s
    Log    Navegador aberto para o frontend em ${url}.

User Login
    [Arguments]    ${username}    ${password}
    Wait Until Page Contains Element    css:input[type="email"]    timeout=10s
    Input Text    css:input[type="email"]    ${username}
    Input Text    css:input[type="password"]    ${password}
    Click Button    xpath=//button[normalize-space()='CONECTAR']  # <--- CORREÇÃO: Usando XPath
    Wait Until Location Contains    ${FRONTEND_URL}/dashboard  timeout=10s
    Page Should Contain    Dashboard
    Log    Login realizado com sucesso para o usuário ${username}.

Navigate To User Management
    Click Link    xpath=//a[normalize-space()='Gerenciamento de Usuários']  # <--- CORREÇÃO: Usando XPath
    Wait Until Page Contains    Gerenciamento de Usuários    timeout=10s
    Page Should Contain    Gerenciamento de Usuários
    Log    Navegado para a tela de Gerenciamento de Usuários.