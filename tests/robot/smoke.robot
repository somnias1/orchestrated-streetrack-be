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
    Length Should Be    ${r.json()}    minimum=1
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
    Length Should Be    ${r.json()}    minimum=1
    ${r}=    GET On Session    api    /hangouts/${hid}    headers=${headers}
    Status Should Be    200    ${r}
    Should Be Equal    ${r.json()}[name]    Robot Hangout

Protected endpoint without token returns 401
    Create Session    api    ${BASE_URL}
    ${r}=    GET On Session    api    /categories/    expected_status=any
    Status Should Be    401    ${r}
