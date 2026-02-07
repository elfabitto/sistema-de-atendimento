# Sistema de Gerenciamento de Fila de Atendimento

Sistema web para gerenciar fila de atendimento de solicitações do WhatsApp de forma justa e organizada.

## 📋 Funcionalidades

- ✅ Sistema de login para colaboradores
- ✅ Entrada/saída da fila de atendimento
- ✅ Distribuição circular e justa de solicitações
- ✅ Notificações em tempo real
- ✅ Timer de 20 minutos para atendimento
- ✅ Painel de estatísticas completo
- ✅ Interface responsiva (mobile-friendly)

## 🚀 Tecnologias Utilizadas

- **Backend**: Flask + Flask-SocketIO
- **Banco de Dados**: SQLite (dev) / PostgreSQL (prod)
- **Frontend**: HTML5, Tailwind CSS, JavaScript
- **Tempo Real**: Socket.IO
- **Autenticação**: Flask-Login
- **Agendamento**: APScheduler

## 📦 Instalação

### Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

### Passo a Passo

1. **Clone o repositório**
```bash
git clone <seu-repositorio>
cd sistema-de-atendimento
```

2. **Crie um ambiente virtual**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Instale as dependências**
```bash
pip install -r requirements.txt
```

4. **Configure as variáveis de ambiente**
```bash
# Copie o arquivo de exemplo
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac

# Edite o arquivo .env com suas configurações
```

5. **Inicialize o banco de dados**
```bash
python init_db.py
```

6. **Execute a aplicação**
```bash
python run.py
```

7. **Acesse no navegador**
```
http://localhost:5000
```

## 👤 Usuários Padrão

Após inicializar o banco de dados, você pode fazer login com:

- **Email**: admin@empresa.com
- **Senha**: admin123

- **Email**: colaborador1@empresa.com
- **Senha**: senha123

- **Email**: colaborador2@empresa.com
- **Senha**: senha123

⚠️ **IMPORTANTE**: Altere essas senhas em produção!

## 📖 Como Usar

### Para Colaboradores

1. **Login**: Acesse com seu email e senha
2. **Entrar na Fila**: Clique em "Entrar na Fila" quando estiver disponível
3. **Receber Solicitação**: Aguarde sua vez na fila
4. **Atender**: 
   - Clique em "ATENDER" para aceitar a solicitação
   - Você tem 20 minutos para responder
   - Clique em "ENCERRAR" ao finalizar
5. **Pular**: Use apenas se realmente não puder atender
6. **Sair da Fila**: Clique em "Sair da Fila" ao encerrar o expediente

### Para Administradores

1. **Criar Solicitações**: Adicione novas solicitações do WhatsApp
2. **Visualizar Estatísticas**: Acompanhe o desempenho da equipe
3. **Gerenciar Colaboradores**: Adicione ou remova usuários

## 🗂️ Estrutura do Projeto

```
sistema-de-atendimento/
├── app/
│   ├── __init__.py           # Inicialização do Flask
│   ├── models.py             # Modelos do banco de dados
│   ├── routes.py             # Rotas principais
│   ├── auth.py               # Autenticação
│   ├── fila.py               # Lógica da fila circular
│   ├── socket_events.py      # Eventos em tempo real
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css     # Estilos customizados
│   │   └── js/
│   │       └── app.js        # JavaScript principal
│   └── templates/
│       ├── base.html         # Template base
│       ├── login.html        # Página de login
│       ├── dashboard.html    # Dashboard principal
│       └── estatisticas.html # Página de estatísticas
├── migrations/               # Migrações do banco
├── requirements.txt          # Dependências Python
├── config.py                 # Configurações
├── .env.example              # Exemplo de variáveis de ambiente
├── .gitignore               # Arquivos ignorados pelo Git
├── init_db.py               # Script de inicialização do BD
├── run.py                   # Arquivo principal
└── README.md                # Este arquivo
```

## 🔧 Configuração

### Variáveis de Ambiente (.env)

```env
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=sua-chave-secreta-aqui
DATABASE_URL=sqlite:///atendimento.db
TIMEOUT_MINUTOS=20
```

### Banco de Dados

O sistema usa SQLite por padrão para desenvolvimento. Para produção, configure PostgreSQL:

```env
DATABASE_URL=postgresql://usuario:senha@localhost/atendimento
```

## 📊 Estatísticas Disponíveis

- Total de atendimentos por colaborador
- Tempo médio de atendimento
- Quantidade de solicitações puladas
- Taxa de conclusão
- Histórico completo de atendimentos

## 🚀 Deploy

### Render.com (Recomendado - Gratuito)

1. Crie uma conta no [Render.com](https://render.com)
2. Conecte seu repositório GitHub
3. Configure as variáveis de ambiente
4. Deploy automático!

### Configurações para Produção

- Use PostgreSQL ao invés de SQLite
- Configure `FLASK_ENV=production`
- Use uma `SECRET_KEY` forte e única
- Configure HTTPS

## 🔐 Segurança

- Senhas são hasheadas com Werkzeug
- Sessões seguras com Flask-Login
- CSRF protection habilitado
- Validação de entrada de dados

## 🐛 Troubleshooting

### Erro ao instalar eventlet no Windows

```bash
pip install eventlet --no-binary :all:
```

### Banco de dados não inicializa

```bash
# Delete o arquivo do banco e recrie
rm instance/atendimento.db  # Linux/Mac
del instance\atendimento.db  # Windows

python init_db.py
```

### SocketIO não conecta

- Verifique se o eventlet está instalado
- Confirme que a porta 5000 está livre
- Limpe o cache do navegador

## 📝 Próximas Funcionalidades

- [ ] Integração com WhatsApp Business API
- [ ] Notificações por email
- [ ] Relatórios em PDF
- [ ] Dashboard de métricas em tempo real
- [ ] Sistema de prioridades para solicitações
- [ ] Chat interno entre colaboradores

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/NovaFuncionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/NovaFuncionalidade`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

## 📧 Contato


---

