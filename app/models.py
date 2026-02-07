"""
Modelos do banco de dados para o sistema de fila de atendimento
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class Colaborador(UserMixin, db.Model):
    """Modelo para colaboradores/usuários do sistema"""
    __tablename__ = 'colaboradores'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    senha_hash = db.Column(db.String(255), nullable=False)
    
    # Status do colaborador
    esta_disponivel = db.Column(db.Boolean, default=False)
    esta_em_atendimento = db.Column(db.Boolean, default=False)
    posicao_fila = db.Column(db.Integer, nullable=True)
    
    # Timestamps
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    atendimentos = db.relationship('Atendimento', backref='colaborador', lazy='dynamic')
    
    def set_senha(self, senha):
        """Define a senha do colaborador (hash)"""
        self.senha_hash = generate_password_hash(senha)
    
    def verificar_senha(self, senha):
        """Verifica se a senha está correta"""
        return check_password_hash(self.senha_hash, senha)
    
    def entrar_na_fila(self):
        """Marca o colaborador como disponível e adiciona à fila"""
        self.esta_disponivel = True
        self.esta_em_atendimento = False
        # A posição será definida pela lógica da fila
    
    def sair_da_fila(self):
        """Remove o colaborador da fila"""
        self.esta_disponivel = False
        self.esta_em_atendimento = False
        self.posicao_fila = None
    
    def iniciar_atendimento(self):
        """Marca o colaborador como em atendimento"""
        self.esta_em_atendimento = True
    
    def finalizar_atendimento(self):
        """Marca o colaborador como disponível novamente"""
        self.esta_em_atendimento = False
    
    def get_estatisticas(self):
        """Retorna estatísticas do colaborador"""
        atendimentos_concluidos = self.atendimentos.filter_by(status='concluido').all()
        atendimentos_pulados = self.atendimentos.filter_by(foi_pulado=True).count()
        
        total_atendimentos = len(atendimentos_concluidos)
        
        if total_atendimentos > 0:
            tempo_total = sum([a.duracao.total_seconds() for a in atendimentos_concluidos if a.duracao])
            tempo_medio = tempo_total / total_atendimentos / 60  # em minutos
        else:
            tempo_medio = 0
        
        return {
            'total_atendimentos': total_atendimentos,
            'total_pulados': atendimentos_pulados,
            'tempo_medio_minutos': round(tempo_medio, 2)
        }
    
    def __repr__(self):
        return f'<Colaborador {self.nome}>'


class Solicitacao(db.Model):
    """Modelo para solicitações de atendimento"""
    __tablename__ = 'solicitacoes'
    
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.Text, nullable=False)
    cliente_nome = db.Column(db.String(100))
    cliente_telefone = db.Column(db.String(20))
    
    # Status: pendente, em_atendimento, concluido, pulado
    status = db.Column(db.String(20), default='pendente', index=True)
    
    # Timestamps
    criado_em = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    atendimentos = db.relationship('Atendimento', backref='solicitacao', lazy='dynamic')
    
    def get_atendimento_atual(self):
        """Retorna o atendimento atual (se houver)"""
        return self.atendimentos.filter_by(status='em_atendimento').first()
    
    def get_historico_atendimentos(self):
        """Retorna histórico de atendimentos desta solicitação"""
        return self.atendimentos.order_by(Atendimento.inicio.desc()).all()
    
    def __repr__(self):
        return f'<Solicitacao {self.id} - {self.status}>'


class Atendimento(db.Model):
    """Modelo para registro de atendimentos"""
    __tablename__ = 'atendimentos'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Chaves estrangeiras
    solicitacao_id = db.Column(db.Integer, db.ForeignKey('solicitacoes.id'), nullable=False)
    colaborador_id = db.Column(db.Integer, db.ForeignKey('colaboradores.id'), nullable=False)
    
    # Status: em_atendimento, concluido, timeout, pulado
    status = db.Column(db.String(20), default='em_atendimento')
    
    # Timestamps
    inicio = db.Column(db.DateTime, default=datetime.utcnow)
    fim = db.Column(db.DateTime, nullable=True)
    duracao = db.Column(db.Interval, nullable=True)
    
    # Flags
    foi_pulado = db.Column(db.Boolean, default=False)
    foi_timeout = db.Column(db.Boolean, default=False)
    
    # Observações
    observacoes = db.Column(db.Text)
    
    def finalizar(self, foi_pulado=False, foi_timeout=False, observacoes=None):
        """Finaliza o atendimento"""
        self.fim = datetime.utcnow()
        self.duracao = self.fim - self.inicio
        self.foi_pulado = foi_pulado
        self.foi_timeout = foi_timeout
        
        if foi_pulado:
            self.status = 'pulado'
        elif foi_timeout:
            self.status = 'timeout'
        else:
            self.status = 'concluido'
        
        if observacoes:
            self.observacoes = observacoes
    
    def get_duracao_minutos(self):
        """Retorna a duração em minutos"""
        if self.duracao:
            return round(self.duracao.total_seconds() / 60, 2)
        elif self.inicio:
            duracao_atual = datetime.utcnow() - self.inicio
            return round(duracao_atual.total_seconds() / 60, 2)
        return 0
    
    def __repr__(self):
        return f'<Atendimento {self.id} - Solicitacao {self.solicitacao_id}>'


class ConfiguracaoSistema(db.Model):
    """Modelo para configurações do sistema"""
    __tablename__ = 'configuracoes_sistema'
    
    id = db.Column(db.Integer, primary_key=True)
    chave = db.Column(db.String(50), unique=True, nullable=False)
    valor = db.Column(db.String(255))
    descricao = db.Column(db.String(255))
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @staticmethod
    def get_valor(chave, padrao=None):
        """Obtém um valor de configuração"""
        config = ConfiguracaoSistema.query.filter_by(chave=chave).first()
        return config.valor if config else padrao
    
    @staticmethod
    def set_valor(chave, valor, descricao=None):
        """Define um valor de configuração"""
        config = ConfiguracaoSistema.query.filter_by(chave=chave).first()
        if config:
            config.valor = valor
            if descricao:
                config.descricao = descricao
        else:
            config = ConfiguracaoSistema(chave=chave, valor=valor, descricao=descricao)
            db.session.add(config)
        db.session.commit()
    
    def __repr__(self):
        return f'<ConfiguracaoSistema {self.chave}={self.valor}>'
