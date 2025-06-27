***Settings***
Resource    ./common_keywords.robot

***Keywords***
Add New User Via UI
    [Arguments]    ${email}    ${password}    ${name}    ${role}    ${phone}
    Click Button    xpath=//button[normalize-space()='Adicionar Novo Usuário']    # <--- CORREÇÃO: Usando XPath
    Wait Until Page Contains    Cadastro de Usuário    timeout=5s
    Input Text    id:emailInput    ${email}
    Input Text    id:passwordInput    ${password}
    Input Text    id:nameInput    ${name}
    Input Text    id:roleInput    ${role}
    Input Text    id:phoneInput    ${phone}
    Click Button    xpath=//button[normalize-space()='Salvar Usuário']  # <--- CORREÇÃO: Usando XPath
    Wait Until Page Contains    Usuário cadastrado com sucesso!    timeout=10s
    Page Should Contain    ${name}
    Log    Usuário '${name}' adicionado com sucesso.

Verify User Exists In List
    [Arguments]    ${name}
    Wait Until Page Contains    ${name}    timeout=5s
    Page Should Contain    ${name}
    Log    Verificado: Usuário '${name}' existe na lista.

Edit User Via UI
    [Arguments]    ${user_name_to_find}    ${new_phone}    ${new_role}
    Click Element    xpath://td[normalize-space()='${user_name_to_find}']/following-sibling::td/button[normalize-space()='Editar']
    Wait Until Page Contains    Editar Usuário    timeout=5s
    Input Text    id:phoneInput    ${new_phone}
    Input Text    id:roleInput    ${new_role}
    Click Button    xpath=//button[normalize-space()='Salvar Alterações']  # <--- CORREÇÃO: Usando XPath
    Wait Until Page Contains    Usuário atualizado com sucesso!    timeout=10s
    Page Should Contain    ${new_phone}
    Page Should Contain    ${new_role}
    Log    Usuário '${user_name_to_find}' editado com sucesso.

Delete User Via UI
    [Arguments]    ${user_name_to_delete}
    Click Element    xpath://td[normalize-space()='${user_name_to_delete}']/following-sibling::td/button[normalize-space()='Excluir']
    Handle Alert    ACCEPT    timeout=5s
    Wait Until Page Does Not Contain    ${user_name_to_delete}    timeout=10s
    Page Should Not Contain    ${user_name_to_delete}
    Log    Usuário '${user_name_to_delete}' deletado com sucesso.