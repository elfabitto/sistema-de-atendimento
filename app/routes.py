"""
Rotas principais da aplicação
"""
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app.models import db, Colaborador, Solicitacao, Atendimento
from app.fila import GerenciadorFila

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Página inicial - redireciona para login ou dashboard"""
    if current_user.is_authenticated:
        # Obtém informações da fila
        fila = GerenciadorFila.obter_fila_completa()
        colaboradores_atendendo = GerenciadorFila.obter_colaboradores_em_atendimento()
        
        # Obtém solicitações pendentes
        solicitacoes_pendentes = Solicitacao.query.filter_by(status='pendente').order_by(
            Solicitacao.criado_em.desc()
        ).limit(10).all()
        
        # Obtém atendimento atual do colaborador (se houver)
        atendimento_atual = None
        if current_user.esta_em_atendimento:
            atendimento_atual = Atendimento.query.filter_by(
                colaborador_id=current_user.id,
                status='em_atendimento'
            ).first()
        
        # Estatísticas do colaborador
        estatisticas = current_user.get_estatisticas()
        
        return render_template(
            'dashboard.html',
            fila=fila,
            colaboradores_atendendo=colaboradores_atendendo,
            solicitacoes_pendentes=solicitacoes_pendentes,
            atendimento_atual=atendimento_atual,
            estatisticas=estatisticas
        )
    return render_template('login.html')


@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard principal do colaborador"""
    # Obtém informações da fila
    fila = GerenciadorFila.obter_fila_completa()
    colaboradores_atendendo = GerenciadorFila.obter_colaboradores_em_atendimento()
    
    # Obtém solicitações pendentes
    solicitacoes_pendentes = Solicitacao.query.filter_by(status='pendente').order_by(
        Solicitacao.criado_em.desc()
    ).limit(10).all()
    
    # Obtém atendimento atual do colaborador (se houver)
    atendimento_atual = None
    if current_user.esta_em_atendimento:
        atendimento_atual = Atendimento.query.filter_by(
            colaborador_id=current_user.id,
            status='em_atendimento'
        ).first()
    
    # Estatísticas do colaborador
    estatisticas = current_user.get_estatisticas()
    
    return render_template(
        'dashboard.html',
        fila=fila,
        colaboradores_atendendo=colaboradores_atendendo,
        solicitacoes_pendentes=solicitacoes_pendentes,
        atendimento_atual=atendimento_atual,
        estatisticas=estatisticas
    )


@main_bp.route('/estatisticas')
@login_required
def estatisticas():
    """Página de estatísticas gerais"""
    # Estatísticas gerais do sistema
    stats_gerais = GerenciadorFila.obter_estatisticas_gerais()
    
    # Ranking de colaboradores por atendimentos
    colaboradores = Colaborador.query.all()
    ranking = []
    
    for colaborador in colaboradores:
        stats = colaborador.get_estatisticas()
        ranking.append({
            'colaborador': colaborador,
            'total_atendimentos': stats['total_atendimentos'],
            'total_pulados': stats['total_pulados'],
            'tempo_medio': stats['tempo_medio_minutos']
        })
    
    # Ordena por total de atendimentos
    ranking.sort(key=lambda x: x['total_atendimentos'], reverse=True)
    
    # Histórico recente de atendimentos
    historico = Atendimento.query.filter(
        Atendimento.status.in_(['concluido', 'pulado', 'timeout'])
    ).order_by(Atendimento.fim.desc()).limit(20).all()
    
    return render_template(
        'estatisticas.html',
        stats_gerais=stats_gerais,
        ranking=ranking,
        historico=historico
    )


@main_bp.route('/solicitacoes')
@login_required
def listar_solicitacoes():
    """Lista todas as solicitações"""
    status_filtro = request.args.get('status', 'todas')
    
    query = Solicitacao.query
    
    if status_filtro != 'todas':
        query = query.filter_by(status=status_filtro)
    
    solicitacoes = query.order_by(Solicitacao.criado_em.desc()).all()
    
    return render_template(
        'solicitacoes.html',
        solicitacoes=solicitacoes,
        status_filtro=status_filtro
    )


@main_bp.route('/solicitacao/<int:solicitacao_id>')
@login_required
def detalhes_solicitacao(solicitacao_id):
    """Detalhes de uma solicitação específica"""
    solicitacao = Solicitacao.query.get_or_404(solicitacao_id)
    historico = solicitacao.get_historico_atendimentos()
    
    return render_template(
        'detalhes_solicitacao.html',
        solicitacao=solicitacao,
        historico=historico
    )


# API Endpoints (JSON)

@main_bp.route('/api/fila')
@login_required
def api_fila():
    """Retorna o estado atual da fila (JSON)"""
    fila = GerenciadorFila.obter_fila_completa()
    
    return jsonify({
        'fila': [{
            'id': c.id,
            'nome': c.nome,
            'posicao': c.posicao_fila,
            'em_atendimento': c.esta_em_atendimento
        } for c in fila]
    })


@main_bp.route('/api/estatisticas')
@login_required
def api_estatisticas():
    """Retorna estatísticas gerais (JSON)"""
    stats = GerenciadorFila.obter_estatisticas_gerais()
    return jsonify(stats)


@main_bp.route('/api/minhas-estatisticas')
@login_required
def api_minhas_estatisticas():
    """Retorna estatísticas do colaborador atual (JSON)"""
    stats = current_user.get_estatisticas()
    return jsonify(stats)


@main_bp.route('/api/solicitacoes/pendentes')
@login_required
def api_solicitacoes_pendentes():
    """Retorna solicitações pendentes (JSON)"""
    solicitacoes = Solicitacao.query.filter_by(status='pendente').order_by(
        Solicitacao.criado_em.desc()
    ).all()
    
    return jsonify({
        'solicitacoes': [{
            'id': s.id,
            'descricao': s.descricao,
            'cliente_nome': s.cliente_nome,
            'cliente_telefone': s.cliente_telefone,
            'criado_em': s.criado_em.isoformat()
        } for s in solicitacoes]
    })


@main_bp.route('/api/atendimento/atual')
@login_required
def api_atendimento_atual():
    """Retorna o atendimento atual do colaborador (JSON)"""
    if not current_user.esta_em_atendimento:
        return jsonify({'atendimento': None})
    
    atendimento = Atendimento.query.filter_by(
        colaborador_id=current_user.id,
        status='em_atendimento'
    ).first()
    
    if not atendimento:
        return jsonify({'atendimento': None})
    
    return jsonify({
        'atendimento': {
            'id': atendimento.id,
            'solicitacao_id': atendimento.solicitacao_id,
            'descricao': atendimento.solicitacao.descricao,
            'cliente_nome': atendimento.solicitacao.cliente_nome,
            'cliente_telefone': atendimento.solicitacao.cliente_telefone,
            'inicio': atendimento.inicio.isoformat(),
            'duracao_minutos': atendimento.get_duracao_minutos()
        }
    })


# Rotas de ação (POST)

@main_bp.route('/api/entrar-fila', methods=['POST'])
@login_required
def api_entrar_fila():
    """Adiciona o colaborador à fila"""
    sucesso = GerenciadorFila.adicionar_colaborador(current_user.id)
    
    if sucesso:
        return jsonify({'sucesso': True, 'mensagem': 'Você entrou na fila'})
    else:
        return jsonify({'sucesso': False, 'mensagem': 'Não foi possível entrar na fila'}), 400


@main_bp.route('/api/sair-fila', methods=['POST'])
@login_required
def api_sair_fila():
    """Remove o colaborador da fila"""
    sucesso = GerenciadorFila.remover_colaborador(current_user.id)
    
    if sucesso:
        return jsonify({'sucesso': True, 'mensagem': 'Você saiu da fila'})
    else:
        return jsonify({'sucesso': False, 'mensagem': 'Não foi possível sair da fila'}), 400


@main_bp.route('/api/criar-solicitacao', methods=['POST'])
@login_required
def api_criar_solicitacao():
    """Cria uma nova solicitação"""
    data = request.get_json()
    
    descricao = data.get('descricao')
    cliente_nome = data.get('cliente_nome')
    cliente_telefone = data.get('cliente_telefone')
    
    if not descricao:
        return jsonify({'sucesso': False, 'mensagem': 'Descrição é obrigatória'}), 400
    
    # Cria a solicitação
    solicitacao = Solicitacao(
        descricao=descricao,
        cliente_nome=cliente_nome,
        cliente_telefone=cliente_telefone,
        status='pendente'
    )
    db.session.add(solicitacao)
    db.session.commit()
    
    # Distribui para o próximo colaborador
    colaborador = GerenciadorFila.distribuir_solicitacao(solicitacao.id)
    
    if colaborador:
        return jsonify({
            'sucesso': True,
            'mensagem': f'Solicitação distribuída para {colaborador.nome}',
            'solicitacao_id': solicitacao.id,
            'colaborador_id': colaborador.id
        })
    else:
        return jsonify({
            'sucesso': True,
            'mensagem': 'Solicitação criada, mas não há colaboradores disponíveis',
            'solicitacao_id': solicitacao.id
        })


@main_bp.route('/api/aceitar-atendimento', methods=['POST'])
@login_required
def api_aceitar_atendimento():
    """Aceita um atendimento"""
    data = request.get_json()
    solicitacao_id = data.get('solicitacao_id')
    
    if not solicitacao_id:
        return jsonify({'sucesso': False, 'mensagem': 'ID da solicitação não fornecido'}), 400
    
    sucesso = GerenciadorFila.aceitar_atendimento(current_user.id, solicitacao_id)
    
    if sucesso:
        return jsonify({'sucesso': True, 'mensagem': 'Atendimento aceito'})
    else:
        return jsonify({'sucesso': False, 'mensagem': 'Não foi possível aceitar o atendimento'}), 400


@main_bp.route('/api/finalizar-atendimento', methods=['POST'])
@login_required
def api_finalizar_atendimento():
    """Finaliza um atendimento"""
    data = request.get_json()
    solicitacao_id = data.get('solicitacao_id')
    observacoes = data.get('observacoes')
    
    if not solicitacao_id:
        return jsonify({'sucesso': False, 'mensagem': 'ID da solicitação não fornecido'}), 400
    
    sucesso = GerenciadorFila.finalizar_atendimento(current_user.id, solicitacao_id, observacoes)
    
    if sucesso:
        return jsonify({'sucesso': True, 'mensagem': 'Atendimento finalizado'})
    else:
        return jsonify({'sucesso': False, 'mensagem': 'Não foi possível finalizar o atendimento'}), 400


@main_bp.route('/api/pular-atendimento', methods=['POST'])
@login_required
def api_pular_atendimento():
    """Pula um atendimento"""
    data = request.get_json()
    solicitacao_id = data.get('solicitacao_id')
    
    if not solicitacao_id:
        return jsonify({'sucesso': False, 'mensagem': 'ID da solicitação não fornecido'}), 400
    
    proximo = GerenciadorFila.pular_atendimento(current_user.id, solicitacao_id)
    
    if proximo:
        return jsonify({
            'sucesso': True,
            'mensagem': f'Atendimento passado para {proximo.nome}',
            'proximo_colaborador': proximo.nome
        })
    else:
        return jsonify({'sucesso': False, 'mensagem': 'Não foi possível pular o atendimento'}), 400
