import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import joblib

# Carregar os dados
df = pd.read_csv('dados_pacientes.csv')

# Separar pressão arterial em duas colunas numéricas
df[['pressao_sistolica', 'pressao_diastolica']] = df['pressao_arterial'].str.split('/', expand=True)
df['pressao_sistolica'] = pd.to_numeric(df['pressao_sistolica'])
df['pressao_diastolica'] = pd.to_numeric(df['pressao_diastolica'])

# Remover coluna original de pressão arterial
df.drop(columns=['pressao_arterial'], inplace=True)

# Codificar variáveis categóricas
categorical_cols = ['sexo', 'sintomas', 'comorbidades', 'alergias']

le_dict = {}
for col in categorical_cols:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col])
    le_dict[col] = le

# Separar features e target (diagnostico)
X = df.drop(columns=['nome', 'diagnostico'])  # nome não entra como feature
y = df['diagnostico']

# Codificar o target (diagnóstico)
le_diag = LabelEncoder()
y = le_diag.fit_transform(y)

# Salvar o label encoder do diagnóstico para usar depois na API
joblib.dump(le_diag, 'le_diagnostico.pkl')

# Dividir treino e teste
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Treinar modelo Random Forest
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Avaliar acurácia
print(f'Acurácia teste: {model.score(X_test, y_test)*100:.2f}%')

# Salvar modelo e label encoders
joblib.dump(model, 'modelo_rf.pkl')
joblib.dump(le_dict, 'label_encoders.pkl')
