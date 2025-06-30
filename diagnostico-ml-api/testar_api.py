import requests

url = 'http://127.0.0.1:5000/diagnostico'

dados = {
    "sexo": "feminino",
    "sintomas": "tosse",
    "comorbidades": "asma",
    "alergias": "nenhuma",
    "temperatura": 37.5,
    "pressao_sistolica": 120,
    "pressao_diastolica": 80,
    "frequencia_cardiaca": 80
}

response = requests.post(url, json=dados)

if response.status_code == 200:
    print("Resposta da API:", response.json())
else:
    print("Erro:", response.status_code, response.text)
