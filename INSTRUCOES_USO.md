# 🚀 Instruções de Uso - Sistema de Fila de Atendimento

## 📋 Índice
1. [Instalação](#instalação)
2. [Configuração](#configuração)
3. [Inicialização](#inicialização)
4. [Como Usar](#como-usar)
5. [Funcionalidades](#funcionalidades)
6. [Solução de Problemas](#solução-de-problemas)

---

## 📦 Instalação

### 1. Criar Ambiente Virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 2. Instalar Dependências

```bash
pip install -r requirements.txt
```

**Nota para Windows**: Se houver erro ao instalar `eventlet`, tente:
```bash
pip install eventlet --no-binary :all:
```

---

## ⚙️ Configuração

### 1. Arquivo .env

O arquivo `.env` já está criado com configurações padrão. Você pode editá-lo se necessário:

```env
FLASK_ENV=development
SECRET_KEY=dev-secret-key-change-in-production-12345
DATABASE_URL=sqlite:///atendimento.db
TIMEOUT_MINUTOS=20
PORT=5000
```

⚠️ **IMPORTANTE**: Em produção, altere a `SECRET_KEY` para uma chave segura!

---

## 🎯 Inicialização

### 1. Inicializar Banco de Dados

```bash
python init_db.py
```

Este comando irá:
- Criar todas as tabelas necessárias
- Criar usuários de exemplo
- Criar solicitações de exemplo

### 2. Iniciar o Servidor

```bash
python run.py
```

O servidor estará disponível em: **http://localhost:5000**

---

## 👤 Como Usar

### Credenciais de Acesso

Após inicializar o banco de dados, você pode fazer login com:

**Administrador:**
- Email: `admin@empresa.com`
- Senha: `admin123`

**Colaboradores de Exemplo:**
- Email: `joao@empresa.com` | Senha: `senha123`
- Email: `maria@empresa.com` | Senha: `senha123`
- Email: `pedro@empresa.com` | Senha: `senha123`
- Email: `ana@empresa.com` | Senha: `senha123`

---

## 🎮 Funcionalidades

### 1. Entrar na Fila

1. Faça login no sistema
2. No Dashboard, clique em **"Entrar na Fila"**
3. Você será adicionado ao final da fila
4. Aguarde sua vez para receber solicitações

### 2. Criar Nova Solicitação

1. No Dashboard, clique em **"Nova Solicitação"**
2. Preencha os dados:
   - Nome do Cliente (opcional)
   - Telefone (opcional)
   - Descrição (obrigatório)
3. Clique em **"Criar"**
4. A solicitação será automaticamente distribuída para o próximo colaborador disponível

### 3. Atender Solicitação

Quando você receber uma solicitação:

1. **Notificação**: Você receberá uma notificação no navegador
2. **Visualizar**: A solicitação aparecerá no card "Atendimento em Andamento"
3. **Informações Disponíveis**:
   - Nome do cliente
   - Telefone
   - Descrição da solicitação
   - Tempo decorrido

4. **Ações Disponíveis**:
   - **ENCERRAR**: Finaliza o atendimento (volta ao final da fila)
   - **PULAR**: Passa para o próximo colaborador (use apenas quando necessário)

### 4. Timeout Automático

- Você tem **20 minutos** para responder a uma solicitação
- Após 20 minutos sem ação, a solicitação passa automaticamente para o próximo
- O tempo é monitorado em tempo real

### 5. Sair da Fila

1. Clique em **"Sair da Fila"** quando encerrar o expediente
2. Você não receberá mais solicitações
3. Se estiver em atendimento, finalize antes de sair

### 6. Visualizar Estatísticas

1. Clique em **"Estatísticas"** no menu
2. Visualize:
   - Total de atendimentos por colaborador
   - Tempo médio de atendimento
   - Quantidade de solicitações puladas
   - Ranking de colaboradores
   - Histórico de atendimentos

---

## 🔄 Fluxo de Trabalho Recomendado

### Para Colaboradores:

1. **Início do Expediente**:
   - Fazer login
   - Clicar em "Entrar na Fila"

2. **Durante o Expediente**:
   - Aguardar solicitações
   - Atender quando receber
   - Finalizar após resolver
   - Voltar automaticamente ao final da fila

3. **Fim do Expediente**:
   - Finalizar atendimentos pendentes
   - Clicar em "Sair da Fila"
   - Fazer logout

### Para Administradores:

1. **Gerenciar Solicitações**:
   - Criar novas solicitações do WhatsApp
   - Monitorar distribuição

2. **Acompanhar Desempenho**:
   - Visualizar estatísticas
   - Identificar gargalos
   - Otimizar processos

---

## 🔧 Solução de Problemas

### Problema: Banco de dados não inicializa

**Solução:**
```bash
# Delete o banco existente
del atendimento.db  # Windows
rm atendimento.db   # Linux/Mac

# Recrie
python init_db.py
```

### Problema: Erro ao instalar eventlet

**Solução:**
```bash
pip install eventlet --no-binary :all:
```

### Problema: SocketIO não conecta

**Soluções:**
1. Verifique se o eventlet está instalado
2. Confirme que a porta 5000 está livre
3. Limpe o cache do navegador
4. Reinicie o servidor

### Problema: Notificações não aparecem

**Solução:**
1. Permita notificações no navegador
2. Verifique as configurações de notificação do sistema

### Problema: Timeout não funciona

**Solução:**
1. Verifique se o APScheduler está rodando
2. Confirme a variável `TIMEOUT_MINUTOS` no .env
3. Reinicie o servidor

---

## 📱 Uso em Dispositivos Móveis

O sistema é totalmente responsivo e funciona em:
- Smartphones
- Tablets
- Desktops

**Recomendações:**
- Use Chrome ou Firefox para melhor compatibilidade
- Ative notificações para receber alertas
- Mantenha a tela ativa durante o expediente

---

## 🔐 Segurança

### Em Desenvolvimento:
- Senhas padrão são aceitáveis
- SQLite é suficiente

### Em Produção:
1. **Altere todas as senhas padrão**
2. **Use PostgreSQL** ao invés de SQLite
3. **Configure HTTPS**
4. **Use SECRET_KEY forte e única**
5. **Configure CORS adequadamente**
6. **Ative logs de auditoria**

---

## 🚀 Deploy em Produção

### Render.com (Recomendado - Gratuito)

1. Crie conta no [Render.com](https://render.com)
2. Conecte seu repositório GitHub
3. Configure variáveis de ambiente:
   ```
   FLASK_ENV=production
   SECRET_KEY=sua-chave-super-secreta
   DATABASE_URL=postgresql://...
   ```
4. Deploy automático!

### Configurações Adicionais:

```env
# .env para produção
FLASK_ENV=production
SECRET_KEY=gere-uma-chave-forte-aqui
DATABASE_URL=postgresql://usuario:senha@host:5432/database
TIMEOUT_MINUTOS=20
```

---

## 📞 Suporte

Para dúvidas ou problemas:
1. Consulte este documento
2. Verifique o README.md
3. Revise os logs do servidor
4. Entre em contato com o suporte técnico

---

## 🎉 Pronto para Usar!

Seu sistema está configurado e pronto para uso. Bom trabalho! 🚀

**Próximos Passos Sugeridos:**
- [ ] Testar todas as funcionalidades
- [ ] Treinar a equipe
- [ ] Configurar backup do banco de dados
- [ ] Monitorar uso inicial
- [ ] Coletar feedback dos usuários
- [ ] Planejar melhorias futuras

---

**Desenvolvido com ❤️ para otimizar o atendimento ao cliente**
