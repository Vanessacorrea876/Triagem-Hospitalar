const express = require('express');
const mongoose = require('mongoose');
const bodyParser = require('body-parser');
const cors = require('cors');
const path = require('path');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const axios = require('axios');

const URL_DIAGNOSTICO = process.env.URL_DIAGNOSTICO || 'http://localhost:5000';

const app = express();
const PORT = process.env.PORT || 3000;
const JWT_SECRET = '7g!p2#qR9zX@fV4b^Ws*8LmN3uHdC6Ye';

app.use(cors());
app.use(bodyParser.json());
app.use(express.static(path.join(__dirname, 'public')));

const MONGO_URI = 'mongodb+srv://vanessacorreasm687:8U5gEchG6SvxO6LU@pi.4boxubh.mongodb.net/triagem?retryWrites=true&w=majority';

mongoose.connect(MONGO_URI, {
  useNewUrlParser: true,
  useUnifiedTopology: true,
})
  .then(() => console.log('✅ MongoDB Atlas conectado'))
  .catch((err) => console.error('❌ Erro ao conectar no MongoDB Atlas:', err));

const usuarioSchema = new mongoose.Schema({
  nome: { type: String, required: true, unique: true },
  senha: { type: String, required: true },
});
const Usuario = mongoose.model('Usuario', usuarioSchema);

const pacienteSchema = new mongoose.Schema({
  nome: String,
  idade: Number,
  sexo: String,
  cartaoSUS: String,
  alergias: [String],
  contatoEmergencia: String,
  pressaoArterial: String,
  saturacaoOxigenio: Number,
  temperaturaCorporal: Number,
  frequenciaCardiaca: Number,
  comorbidades: [String],
  usoMedicamento: String,
  email: String,
  endereco: String,
  sintomas: [String],
  risco: String,
  motivo: String,
  dataHora: Date,
});
const Paciente = mongoose.model('Paciente', pacienteSchema);

function autenticarToken(req, res, next) {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];
  if (!token) return res.status(401).json({ message: 'Token não fornecido' });

  jwt.verify(token, JWT_SECRET, (err, usuario) => {
    if (err) return res.status(403).json({ message: 'Token inválido' });
    req.usuario = usuario;
    next();
  });
}

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'formulario.html'));
});

// ROTA LOGIN CORRIGIDA
app.post('/login', async (req, res) => {
  const { nome, senha } = req.body;
  if (!nome || !senha) return res.status(400).json({ message: 'Nome e senha são obrigatórios' });

  try {
    const usuario = await Usuario.findOne({ nome });
    if (!usuario) return res.status(400).json({ message: 'Usuário não encontrado' });

    const senhaValida = await bcrypt.compare(senha, usuario.senha);
    if (!senhaValida) return res.status(400).json({ message: 'Senha incorreta' });

    const token = jwt.sign({ nome: usuario.nome, id: usuario._id }, JWT_SECRET, { expiresIn: '1h' });
    res.json({ token, nome: usuario.nome });  // <-- retorna token + nome do usuário
  } catch (error) {
    res.status(500).json({ message: 'Erro interno no servidor' });
  }
});

app.post('/usuarios', async (req, res) => {
  const { nome, senha } = req.body;
  if (!nome || !senha) return res.status(400).json({ message: 'Nome e senha são obrigatórios' });

  try {
    const hashSenha = await bcrypt.hash(senha, 10);
    const usuario = new Usuario({ nome, senha: hashSenha });
    await usuario.save();
    res.status(201).json({ message: 'Usuário criado com sucesso' });
  } catch (error) {
    if (error.code === 11000) {
      res.status(400).json({ message: 'Usuário já existe' });
    } else {
      res.status(500).json({ message: 'Erro interno no servidor' });
    }
  }
});

app.post('/pacientes', autenticarToken, async (req, res) => {
  try {
    const dados = req.body;

    let pressao_sistolica = 0;
    let pressao_diastolica = 0;
    if (dados.pressaoArterial) {
      const partes = dados.pressaoArterial.split('/');
      if (partes.length === 2) {
        pressao_sistolica = Number(partes[0].trim()) || 0;
        pressao_diastolica = Number(partes[1].trim()) || 0;
      }
    }

    const dadosParaIA = {
      sexo: dados.sexo ? dados.sexo.toLowerCase() : 'nenhuma',
      sintomas: Array.isArray(dados.sintomas) ? dados.sintomas.map(s => s.toLowerCase()) : ['nenhuma'],
      comorbidades: Array.isArray(dados.comorbidades) ? dados.comorbidades.map(c => c.toLowerCase()) : ['nenhuma'],
      alergias: Array.isArray(dados.alergias) ? dados.alergias.map(a => a.toLowerCase()) : ['nenhuma'],
      temperatura: Number(dados.temperaturaCorporal) || 0,
      pressao_sistolica,
      pressao_diastolica,
      frequencia_cardiaca: Number(dados.frequenciaCardiaca) || 0,
    };

    const respostaIA = await axios.post(`${URL_DIAGNOSTICO}/diagnostico`, dadosParaIA);

    dados.risco = respostaIA.data.risco || 'Indefinido';
    dados.motivo = respostaIA.data.motivo || 'Sem motivo';
    dados.dataHora = new Date();

    const paciente = new Paciente(dados);
    await paciente.save();

    res.status(201).json({ message: 'Paciente salvo com sucesso', paciente, diagnostico: respostaIA.data });
  } catch (error) {
    console.error('Erro ao salvar paciente ou consultar IA:', error.message);
    res.status(500).json({ message: 'Erro ao salvar paciente', error: error.message });
  }
});

// Busca paciente pelo ID (útil para editar paciente)
app.get('/triagem/:id', autenticarToken, async (req, res) => {
  try {
    const paciente = await Paciente.findById(req.params.id);
    if (!paciente) return res.status(404).json({ message: 'Paciente não encontrado' });
    res.json(paciente);
  } catch (error) {
    res.status(500).json({ message: 'Erro interno no servidor', error: error.message });
  }
});

// Lista pacientes, com filtro opcional por nome (case-insensitive)
app.get('/pacientes', autenticarToken, async (req, res) => {
  try {
    const filtro = {};
    if (req.query.nome) {
      filtro.nome = { $regex: req.query.nome, $options: 'i' };
    }
    const pacientes = await Paciente.find(filtro).sort({ dataHora: -1 });
    res.json(pacientes);
  } catch (error) {
    res.status(500).json({ message: 'Erro interno no servidor', error: error.message });
  }
});

// Busca paciente por Cartão SUS (mantida, caso queira usar)
app.get('/pacientes/buscar/:cartaoSUS', autenticarToken, async (req, res) => {
  const { cartaoSUS } = req.params;
  try {
    const paciente = await Paciente.findOne({ cartaoSUS });
    if (!paciente) return res.status(404).json({ message: 'Paciente não encontrado' });
    res.json(paciente);
  } catch (error) {
    res.status(500).json({ message: 'Erro ao buscar paciente', error: error.message });
  }
});

app.listen(PORT, () => {
  console.log(`🚀 Servidor rodando na porta ${PORT}`);
});
