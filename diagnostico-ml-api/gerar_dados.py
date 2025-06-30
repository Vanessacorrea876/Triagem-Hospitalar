import random
import pandas as pd

nomes = ['João', 'Maria', 'Carlos', 'Ana', 'Pedro', 'Juliana', 'Ricardo', 'Fernanda', 'Lucas', 'Patrícia']
sobrenomes = ['Silva', 'Oliveira', 'Souza', 'Pereira', 'Lima', 'Costa', 'Alves', 'Dias', 'Santos', 'Gomes']
sexos = ['masculino', 'feminino']
sintomas = ['tosse', 'febre', 'dor de cabeça', 'náusea', 'fadiga']
comorbidades = ['nenhuma', 'diabetes', 'hipertensao', 'asma']
alergias = ['nenhuma', 'penicilina', 'amendoim', 'latex']

def gerar_pressao():
    sistolica = random.randint(90, 160)
    diastolica = random.randint(60, 100)
    return f"{sistolica}/{diastolica}"

dados = []

for i in range(300):
    nome = f"{random.choice(nomes)} {random.choice(sobrenomes)}"
    sexo = random.choice(sexos)
    sintoma = random.choice(sintomas)
    comorbidade = random.choice(comorbidades)
    alergia = random.choice(alergias)
    temperatura = round(random.uniform(36.0, 39.5), 1)
    freq_cardiaca = random.randint(60, 110)
    pressao = gerar_pressao()

    # Diagnóstico baseado simples (só pra variar entre os valores)
    if temperatura > 38.0 or comorbidade != 'nenhuma':
        diagnostico = random.choice(['risco_medio', 'risco_alto'])
    else:
        diagnostico = 'risco_baixo'

    dados.append([nome, sexo, sintoma, comorbidade, alergia, temperatura, freq_cardiaca, pressao, diagnostico])

df = pd.DataFrame(dados, columns=['nome', 'sexo', 'sintomas', 'comorbidades', 'alergias', 'temperatura', 'frequencia_cardiaca', 'pressao_arterial', 'diagnostico'])
df.to_csv('dados_pacientes.csv', index=False)

print("Arquivo dados_pacientes.csv criado com 300 linhas.")
