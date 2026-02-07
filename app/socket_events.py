"""
Eventos SocketIO para comunicação em tempo real
"""
from flask import request
from flask_socketio import emit, join_room, leave_room
from flask_login import current_user
from app.models import db, Colaborador, Solicitacao, Atendimento
from app.fila import GerenciadorFila


def register_socket_events(socketio):
    """Registra todos os eventos SocketIO"""
    
    @socketio.on('connect')
    def handle_connect():
        """Evento de conexão do cliente"""
        if current_user.is_authenticated:
            # Adiciona o colaborador à sua sala pessoal
            join_room(f'colaborador_{current_user.id}')
            
            # Adiciona à sala geral
            join_room('geral')
            
            print(f'Colaborador {current_user.nome} conectado')
            
            # Envia estado atual da fila
            fila = GerenciadorFila.obter_fila_completa()
            emit('atualizar_fila', {
                'fila': [{'id': c.id, 'nome': c.nome, 'posicao': c.posicao_fila} for c in fila]
            })
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Evento de desconexão do cliente"""
        if current_user.is_authenticated:
            leave_room(f'colaborador_{current_user.id}')
            leave_room('geral')
            print(f'Colaborador {current_user.nome} desconectado')
    
    @socketio.on('entrar_fila')
    def handle_entrar_fila():
        """Colaborador entra na fila"""
        if not current_user.is_authenticated:
            emit('erro', {'mensagem': 'Você precisa estar logado'})
            return
        
        sucesso = GerenciadorFila.adicionar_colaborador(current_user.id)
        
        if sucesso:
            # Atualiza a fila para todos
            fila = GerenciadorFila.obter_fila_completa()
            socketio.emit('atualizar_fila', {
                'fila': [{'id': c.id, 'nome': c.nome, 'posicao': c.posicao_fila} for c in fila]
            }, room='geral')
            
            emit('entrou_fila', {'mensagem': 'Você entrou na fila com sucesso!'})
        else:
            emit('erro', {'mensagem': 'Não foi possível entrar na fila'})
    
    @socketio.on('sair_fila')
    def handle_sair_fila():
        """Colaborador sai da fila"""
        if not current_user.is_authenticated:
            emit('erro', {'mensagem': 'Você precisa estar logado'})
            return
        
        sucesso = GerenciadorFila.remover_colaborador(current_user.id)
        
        if sucesso:
            # Atualiza a fila para todos
            fila = GerenciadorFila.obter_fila_completa()
            socketio.emit('atualizar_fila', {
                'fila': [{'id': c.id, 'nome': c.nome, 'posicao': c.posicao_fila} for c in fila]
            }, room='geral')
            
            emit('saiu_fila', {'mensagem': 'Você saiu da fila'})
        else:
            emit('erro', {'mensagem': 'Não foi possível sair da fila'})
    
    @socketio.on('nova_solicitacao')
    def handle_nova_solicitacao(data):
        """Cria uma nova solicitação e distribui para o próximo da fila"""
        if not current_user.is_authenticated:
            emit('erro', {'mensagem': 'Você precisa estar logado'})
            return
        
        descricao = data.get('descricao')
        cliente_nome = data.get('cliente_nome')
        cliente_telefone = data.get('cliente_telefone')
        
        if not descricao:
            emit('erro', {'mensagem': 'Descrição é obrigatória'})
            return
        
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
            # Notifica o colaborador que recebeu a solicitação
            socketio.emit('nova_solicitacao_recebida', {
                'solicitacao_id': solicitacao.id,
                'descricao': solicitacao.descricao,
                'cliente_nome': solicitacao.cliente_nome,
                'cliente_telefone': solicitacao.cliente_telefone,
                'timeout_minutos': 20
            }, room=f'colaborador_{colaborador.id}')
            
            # Atualiza a fila para todos
            fila = GerenciadorFila.obter_fila_completa()
            socketio.emit('atualizar_fila', {
                'fila': [{'id': c.id, 'nome': c.nome, 'posicao': c.posicao_fila, 
                         'em_atendimento': c.esta_em_atendimento} for c in fila]
            }, room='geral')
            
            emit('solicitacao_criada', {
                'mensagem': f'Solicitação distribuída para {colaborador.nome}',
                'solicitacao_id': solicitacao.id
            })
        else:
            emit('aviso', {
                'mensagem': 'Solicitação criada, mas não há colaboradores disponíveis na fila'
            })
    
    @socketio.on('aceitar_atendimento')
    def handle_aceitar_atendimento(data):
        """Colaborador aceita o atendimento"""
        if not current_user.is_authenticated:
            emit('erro', {'mensagem': 'Você precisa estar logado'})
            return
        
        solicitacao_id = data.get('solicitacao_id')
        
        if not solicitacao_id:
            emit('erro', {'mensagem': 'ID da solicitação não fornecido'})
            return
        
        sucesso = GerenciadorFila.aceitar_atendimento(current_user.id, solicitacao_id)
        
        if sucesso:
            # Atualiza a fila para todos
            fila = GerenciadorFila.obter_fila_completa()
            socketio.emit('atualizar_fila', {
                'fila': [{'id': c.id, 'nome': c.nome, 'posicao': c.posicao_fila,
                         'em_atendimento': c.esta_em_atendimento} for c in fila]
            }, room='geral')
            
            # Notifica todos que um atendimento foi iniciado
            socketio.emit('atendimento_iniciado', {
                'colaborador_id': current_user.id,
                'colaborador_nome': current_user.nome,
                'solicitacao_id': solicitacao_id
            }, room='geral')
            
            emit('atendimento_aceito', {
                'mensagem': 'Atendimento aceito com sucesso!',
                'solicitacao_id': solicitacao_id
            })
        else:
            emit('erro', {'mensagem': 'Não foi possível aceitar o atendimento'})
    
    @socketio.on('finalizar_atendimento')
    def handle_finalizar_atendimento(data):
        """Colaborador finaliza o atendimento"""
        if not current_user.is_authenticated:
            emit('erro', {'mensagem': 'Você precisa estar logado'})
            return
        
        solicitacao_id = data.get('solicitacao_id')
        observacoes = data.get('observacoes')
        
        if not solicitacao_id:
            emit('erro', {'mensagem': 'ID da solicitação não fornecido'})
            return
        
        sucesso = GerenciadorFila.finalizar_atendimento(
            current_user.id, 
            solicitacao_id, 
            observacoes
        )
        
        if sucesso:
            # Atualiza a fila para todos
            fila = GerenciadorFila.obter_fila_completa()
            socketio.emit('atualizar_fila', {
                'fila': [{'id': c.id, 'nome': c.nome, 'posicao': c.posicao_fila,
                         'em_atendimento': c.esta_em_atendimento} for c in fila]
            }, room='geral')
            
            emit('atendimento_finalizado', {
                'mensagem': 'Atendimento finalizado com sucesso!',
                'solicitacao_id': solicitacao_id
            })
            
            # Atualiza estatísticas
            socketio.emit('atualizar_estatisticas', {}, room='geral')
        else:
            emit('erro', {'mensagem': 'Não foi possível finalizar o atendimento'})
    
    @socketio.on('pular_atendimento')
    def handle_pular_atendimento(data):
        """Colaborador pula o atendimento"""
        if not current_user.is_authenticated:
            emit('erro', {'mensagem': 'Você precisa estar logado'})
            return
        
        solicitacao_id = data.get('solicitacao_id')
        
        if not solicitacao_id:
            emit('erro', {'mensagem': 'ID da solicitação não fornecido'})
            return
        
        proximo_colaborador = GerenciadorFila.pular_atendimento(
            current_user.id, 
            solicitacao_id
        )
        
        if proximo_colaborador:
            # Busca a solicitação atualizada
            solicitacao = Solicitacao.query.get(solicitacao_id)
            
            # Notifica o próximo colaborador
            socketio.emit('nova_solicitacao_recebida', {
                'solicitacao_id': solicitacao.id,
                'descricao': solicitacao.descricao,
                'cliente_nome': solicitacao.cliente_nome,
                'cliente_telefone': solicitacao.cliente_telefone,
                'timeout_minutos': 20
            }, room=f'colaborador_{proximo_colaborador.id}')
            
            # Atualiza a fila para todos
            fila = GerenciadorFila.obter_fila_completa()
            socketio.emit('atualizar_fila', {
                'fila': [{'id': c.id, 'nome': c.nome, 'posicao': c.posicao_fila,
                         'em_atendimento': c.esta_em_atendimento} for c in fila]
            }, room='geral')
            
            emit('atendimento_pulado', {
                'mensagem': f'Atendimento passado para {proximo_colaborador.nome}',
                'solicitacao_id': solicitacao_id
            })
            
            # Atualiza estatísticas
            socketio.emit('atualizar_estatisticas', {}, room='geral')
        else:
            emit('erro', {'mensagem': 'Não foi possível pular o atendimento'})
    
    @socketio.on('obter_estatisticas')
    def handle_obter_estatisticas():
        """Retorna estatísticas gerais do sistema"""
        if not current_user.is_authenticated:
            emit('erro', {'mensagem': 'Você precisa estar logado'})
            return
        
        estatisticas = GerenciadorFila.obter_estatisticas_gerais()
        emit('estatisticas', estatisticas)
    
    @socketio.on('obter_minhas_estatisticas')
    def handle_obter_minhas_estatisticas():
        """Retorna estatísticas do colaborador atual"""
        if not current_user.is_authenticated:
            emit('erro', {'mensagem': 'Você precisa estar logado'})
            return
        
        estatisticas = current_user.get_estatisticas()
        emit('minhas_estatisticas', estatisticas)
