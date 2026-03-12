*** Settings ***
# §6.5: smoke (health, root) + one flow per resource. BASE_URL and optional AUTH_TOKEN from env.
Library    Collections
Library    RequestsLibrary
Library    OperatingSystem

*** Variables ***
${BASE_URL}    http://localhost:8000

*** Test Cases ***
Root returns 200 and message
    Create Session    api    ${BASE_URL}
    ${r}=    GET On Session    api    /
    Status Should Be    200    ${r}
    Dictionary Should Contain Key    ${r.json()}    message
    Should Be Equal    ${r.json()}[message]    Streetrack API

Health returns 200 and status ok
    Create Session    api    ${BASE_URL}
    ${r}=    GET On Session    api    /health
    Status Should Be    200    ${r}
    Dictionary Should Contain Key    ${r.json()}    status
    Should Be Equal    ${r.json()}[status]    ok

Categories flow when AUTH_TOKEN set
    ${token}=    Get Environment Variable    AUTH_TOKEN    default=
    Run Keyword If    '${token}' == ''    Pass Execution    AUTH_TOKEN not set - skipping protected test
    Create Session    api    ${BASE_URL}
    ${headers}=    Create Dictionary    Authorization=Bearer ${token}
    ${body}=    Create Dictionary    name=Robot Cat    is_income=${False}
    ${r}=    POST On Session    api    /categories/    json=${body}    headers=${headers}
    Status Should Be    201    ${r}
    Dictionary Should Contain Key    ${r.json()}    id
    ${cid}=    Set Variable    ${r.json()}[id]
    ${r}=    GET On Session    api    /categories/    headers=${headers}
    Status Should Be    200    ${r}
    ${length}=    Get Length    ${r.json()}
    Should Be True    ${length} >= 1
    ${r}=    GET On Session    api    /categories/${cid}    headers=${headers}
    Status Should Be    200    ${r}
    Should Be Equal    ${r.json()}[name]    Robot Cat

Hangouts flow when AUTH_TOKEN set
    ${token}=    Get Environment Variable    AUTH_TOKEN    default=
    Run Keyword If    '${token}' == ''    Pass Execution    AUTH_TOKEN not set - skipping protected test
    Create Session    api    ${BASE_URL}
    ${headers}=    Create Dictionary    Authorization=Bearer ${token}
    ${body}=    Create Dictionary    name=Robot Hangout    date=2025-06-01
    ${r}=    POST On Session    api    /hangouts/    json=${body}    headers=${headers}
    Status Should Be    201    ${r}
    Dictionary Should Contain Key    ${r.json()}    id
    ${hid}=    Set Variable    ${r.json()}[id]
    ${r}=    GET On Session    api    /hangouts/    headers=${headers}
    Status Should Be    200    ${r}
    ${length}=    Get Length    ${r.json()}
    Should Be True    ${length} >= 1
    ${r}=    GET On Session    api    /hangouts/${hid}    headers=${headers}
    Status Should Be    200    ${r}
    Should Be Equal    ${r.json()}[name]    Robot Hangout

Subcategories flow when AUTH_TOKEN set
    ${token}=    Get Environment Variable    AUTH_TOKEN    default=
    Run Keyword If    '${token}' == ''    Pass Execution    AUTH_TOKEN not set - skipping protected test
    Create Session    api    ${BASE_URL}
    ${headers}=    Create Dictionary    Authorization=Bearer ${token}
    ${cat_body}=    Create Dictionary    name=Robot Parent Cat    is_income=${False}
    ${r}=    POST On Session    api    /categories/    json=${cat_body}    headers=${headers}
    Status Should Be    201    ${r}
    ${cid}=    Set Variable    ${r.json()}[id]
    ${sub_body}=    Create Dictionary    category_id=${cid}    name=Robot Sub    belongs_to_income=${False}
    ${r}=    POST On Session    api    /subcategories/    json=${sub_body}    headers=${headers}
    Status Should Be    201    ${r}
    Dictionary Should Contain Key    ${r.json()}    id
    ${sid}=    Set Variable    ${r.json()}[id]
    ${r}=    GET On Session    api    /subcategories/    headers=${headers}
    Status Should Be    200    ${r}
    ${length}=    Get Length    ${r.json()}
    Should Be True    ${length} >= 1
    ${r}=    GET On Session    api    /subcategories/${sid}    headers=${headers}
    Status Should Be    200    ${r}
    Should Be Equal    ${r.json()}[name]    Robot Sub

Transactions flow when AUTH_TOKEN set
    ${token}=    Get Environment Variable    AUTH_TOKEN    default=
    Run Keyword If    '${token}' == ''    Pass Execution    AUTH_TOKEN not set - skipping protected test
    Create Session    api    ${BASE_URL}
    ${headers}=    Create Dictionary    Authorization=Bearer ${token}
    ${cat_body}=    Create Dictionary    name=Robot Tx Cat    is_income=${False}
    ${r}=    POST On Session    api    /categories/    json=${cat_body}    headers=${headers}
    Status Should Be    201    ${r}
    ${cid}=    Set Variable    ${r.json()}[id]
    ${sub_body}=    Create Dictionary    category_id=${cid}    name=Robot Tx Sub    belongs_to_income=${False}
    ${r}=    POST On Session    api    /subcategories/    json=${sub_body}    headers=${headers}
    Status Should Be    201    ${r}
    ${sid}=    Set Variable    ${r.json()}[id]
    ${tx_value}=    Evaluate    -100
    ${tx_body}=    Create Dictionary    subcategory_id=${sid}    value=${tx_value}    description=Robot transaction    date=2025-06-01
    ${r}=    POST On Session    api    /transactions/    json=${tx_body}    headers=${headers}
    Status Should Be    201    ${r}
    Dictionary Should Contain Key    ${r.json()}    id
    ${tid}=    Set Variable    ${r.json()}[id]
    ${r}=    GET On Session    api    /transactions/    headers=${headers}
    Status Should Be    200    ${r}
    ${length}=    Get Length    ${r.json()}
    Should Be True    ${length} >= 1
    ${r}=    GET On Session    api    /transactions/${tid}    headers=${headers}
    Status Should Be    200    ${r}
    Should Be Equal    ${r.json()}[description]    Robot transaction
    Should Be Equal As Integers    ${r.json()}[value]    -100

Protected endpoint without token returns 401
    Create Session    api    ${BASE_URL}
    ${r}=    GET On Session    api    /categories/    expected_status=any
    Status Should Be    401    ${r}

Dashboard balance returns 200 when AUTH_TOKEN set
    ${token}=    Get Environment Variable    AUTH_TOKEN    default=
    Run Keyword If    '${token}' == ''    Pass Execution    AUTH_TOKEN not set - skipping protected test
    Create Session    api    ${BASE_URL}
    ${headers}=    Create Dictionary    Authorization=Bearer ${token}
    ${r}=    GET On Session    api    /dashboard/balance    headers=${headers}
    Status Should Be    200    ${r}
    Dictionary Should Contain Key    ${r.json()}    balance

Transaction manager export returns 200 when AUTH_TOKEN set
    ${token}=    Get Environment Variable    AUTH_TOKEN    default=
    Run Keyword If    '${token}' == ''    Pass Execution    AUTH_TOKEN not set - skipping protected test
    Create Session    api    ${BASE_URL}
    ${headers}=    Create Dictionary    Authorization=Bearer ${token}
    ${r}=    GET On Session    api    /transaction-manager/export    headers=${headers}
    Status Should Be    200    ${r}
    # Response is text/csv
    Should Contain    ${r.headers}[Content-Type]    text/csv
