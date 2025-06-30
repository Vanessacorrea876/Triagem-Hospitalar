from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import pandas as pd

app = Flask(__name__)
CORS(app)  # Habilita CORS

# Carrega modelo e encoders
model = joblib.load('modelo_rf.pkl')
le_diag = joblib.load('le_diagnostico.pkl')
label_encoders = joblib.load('label_encoders.pkl')

feature_columns = ['sexo', 'sintomas', 'comorbidades', 'alergias',
                   'temperatura', 'pressao_sistolica', 'pressao_diastolica', 'frequencia_cardiaca']

def preprocess_input(data):
    for campo in ['sintomas', 'comorbidades', 'alergias']:
        valor = data.get(campo, 'nenhuma')
        if isinstance(valor, list):
            valor_str = ','.join([str(v).strip().lower() for v in valor])
            data[campo] = valor_str
        elif isinstance(valor, str):
            data[campo] = valor.strip().lower()
        else:
            data[campo] = 'nenhuma'

    sexo_val = data.get('sexo', 'nenhuma')
    data['sexo'] = sexo_val.strip().lower() if isinstance(sexo_val, str) else 'nenhuma'

    df = pd.DataFrame([data])

    for col in feature_columns:
        if col not in df.columns:
            df[col] = 'nenhuma' if col in ['sexo', 'sintomas', 'comorbidades', 'alergias'] else 0

    for col in ['sexo', 'sintomas', 'comorbidades', 'alergias']:
        le = label_encoders.get(col)
        if le:
            valid_values = set(le.classes_)
            def transform_val(val):
                if ',' in val:
                    for part in val.split(','):
                        if part.strip() in valid_values:
                            return part.strip()
                    return 'nenhuma'
                return val if val in valid_values else 'nenhuma'
            df[col] = df[col].apply(transform_val)
            df[col] = le.transform(df[col])

    if hasattr(model, 'feature_names_in_'):
        df = df[list(model.feature_names_in_)]
    else:
        df = df[feature_columns]

    return df

@app.route('/diagnostico', methods=['POST'])
def diagnostico():
    dados = request.json

    # 🔧 Mapa de labels simples para risco + motivo
    mapa_labels = {
        "risco_alto": {
            "risco": "alto",
            "motivo": "sintomas graves ou instabilidade nos sinais vitais"
        },
        "risco_moderado": {
            "risco": "moderado",
            "motivo": "sintomas relevantes, porém estáveis"
        },
        "risco_baixo": {
            "risco": "baixo",
            "motivo": "sintomas leves e sinais vitais normais"
        }
    }

    try:
        X = preprocess_input(dados)
        pred = model.predict(X)
        pred_label = le_diag.inverse_transform(pred)[0].strip().lower()

        # Se estiver no mapa, retorna risco/motivo
        if pred_label in mapa_labels:
            return jsonify(mapa_labels[pred_label])

        # Caso seja "risco: motivo"
        if ':' in pred_label:
            risco, motivo = pred_label.split(':', 1)
            return jsonify({
                'risco': risco.strip().lower(),
                'motivo': motivo.strip()
            })

        # Caso não esteja no mapa nem tenha ":", retorna default
        return jsonify({
            'risco': pred_label,
            'motivo': 'Sem motivo especificado'
        })

    except ValueError as e:
        return jsonify({'erro': str(e)}), 400
    except Exception as e:
        return jsonify({'erro': 'Erro interno: ' + str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
