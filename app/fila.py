"""
Lógica da fila circular de atendimento
"""
from datetime import datetime, timedelta
from app.models import db, Colaborador, Solicitacao, Atendimento
from flask import current_app


class GerenciadorFila:
    """Gerencia a fila circular de atendimento"""
    
    @staticmethod
    def adicionar_colaborador(colaborador_id):
        """
        Adiciona um colaborador à fila
        Retorna True se adicionado com sucesso, False caso contrário
        """
        colaborador = Colaborador.query.get(colaborador_id)
        if not colaborador:
            return False
        
        # Verifica se já está na fila
        if colaborador.esta_disponivel:
            return False
        
        # Marca como disponível
        colaborador.entrar_na_fila()
        
        # Define a posição na fila (última posição)
        ultima_posicao = db.session.query(db.func.max(Colaborador.posicao_fila)).scalar() or 0
        colaborador.posicao_fila = ultima_posicao + 1
        
        db.session.commit()
        return True
    
    @staticmethod
    def remover_colaborador(colaborador_id):
        """
        Remove um colaborador da fila
        Retorna True se removido com sucesso, False caso contrário
        """
        colaborador = Colaborador.query.get(colaborador_id)
        if not colaborador:
            return False
        
        # Guarda a posição antes de remover
        posicao_removida = colaborador.posicao_fila
        
        # Remove da fila
        colaborador.sair_da_fila()
        
        # Reorganiza as posições dos colaboradores que estavam depois
        if posicao_removida:
            colaboradores_depois = Colaborador.query.filter(
                Colaborador.posicao_fila > posicao_removida,
                Colaborador.esta_disponivel == True
            ).all()
            
            for colab in colaboradores_depois:
                colab.posicao_fila -= 1
        
        db.session.commit()
        return True
    
    @staticmethod
    def obter_proximo_colaborador():
        """
        Retorna o próximo colaborador disponível na fila
        (aquele que não está em atendimento e tem a menor posição)
        """
        return Colaborador.query.filter_by(
            esta_disponivel=True,
            esta_em_atendimento=False
        ).order_by(Colaborador.posicao_fila).first()
    
    @staticmethod
    def obter_fila_completa():
        """Retorna todos os colaboradores na fila, ordenados por posição"""
        return Colaborador.query.filter_by(
            esta_disponivel=True
        ).order_by(Colaborador.posicao_fila).all()
    
    @staticmethod
    def obter_colaboradores_em_atendimento():
        """Retorna colaboradores que estão atendendo no momento"""
        return Colaborador.query.filter_by(
            esta_disponivel=True,
            esta_em_atendimento=True
        ).all()
    
    @staticmethod
    def distribuir_solicitacao(solicitacao_id):
        """
        Distribui uma solicitação para o próximo colaborador da fila
        Retorna o colaborador que recebeu a solicitação ou None
        """
        solicitacao = Solicitacao.query.get(solicitacao_id)
        if not solicitacao or solicitacao.status != 'pendente':
            return None
        
        # Obtém o próximo colaborador
        colaborador = GerenciadorFila.obter_proximo_colaborador()
        if not colaborador:
            return None
        
        # Cria o atendimento
        atendimento = Atendimento(
            solicitacao_id=solicitacao_id,
            colaborador_id=colaborador.id,
            status='em_atendimento'
        )
        
        # Atualiza status
        solicitacao.status = 'em_atendimento'
        colaborador.iniciar_atendimento()
        
        db.session.add(atendimento)
        db.session.commit()
        
        return colaborador
    
    @staticmethod
    def aceitar_atendimento(colaborador_id, solicitacao_id):
        """
        Colaborador aceita o atendimento
        Retorna True se aceito com sucesso
        """
        atendimento = Atendimento.query.filter_by(
            colaborador_id=colaborador_id,
            solicitacao_id=solicitacao_id,
            status='em_atendimento'
        ).first()
        
        if not atendimento:
            return False
        
        # Atendimento já está marcado como em_atendimento
        # Apenas confirma que o colaborador aceitou
        db.session.commit()
        return True
    
    @staticmethod
    def finalizar_atendimento(colaborador_id, solicitacao_id, observacoes=None):
        """
        Finaliza um atendimento e retorna o colaborador ao final da fila
        Retorna True se finalizado com sucesso
        """
        colaborador = Colaborador.query.get(colaborador_id)
        solicitacao = Solicitacao.query.get(solicitacao_id)
        
        if not colaborador or not solicitacao:
            return False
        
        # Busca o atendimento atual
        atendimento = Atendimento.query.filter_by(
            colaborador_id=colaborador_id,
            solicitacao_id=solicitacao_id,
            status='em_atendimento'
        ).first()
        
        if not atendimento:
            return False
        
        # Finaliza o atendimento
        atendimento.finalizar(observacoes=observacoes)
        
        # Atualiza status da solicitação
        solicitacao.status = 'concluido'
        
        # Retorna colaborador ao final da fila
        colaborador.finalizar_atendimento()
        
        # Reposiciona no final da fila
        ultima_posicao = db.session.query(db.func.max(Colaborador.posicao_fila)).scalar() or 0
        colaborador.posicao_fila = ultima_posicao + 1
        
        db.session.commit()
        return True
    
    @staticmethod
    def pular_atendimento(colaborador_id, solicitacao_id):
        """
        Colaborador pula o atendimento e passa para o próximo
        Retorna o próximo colaborador que receberá a solicitação
        """
        colaborador = Colaborador.query.get(colaborador_id)
        solicitacao = Solicitacao.query.get(solicitacao_id)
        
        if not colaborador or not solicitacao:
            return None
        
        # Busca o atendimento atual
        atendimento = Atendimento.query.filter_by(
            colaborador_id=colaborador_id,
            solicitacao_id=solicitacao_id,
            status='em_atendimento'
        ).first()
        
        if not atendimento:
            return None
        
        # Marca como pulado
        atendimento.finalizar(foi_pulado=True)
        
        # Retorna colaborador ao final da fila
        colaborador.finalizar_atendimento()
        ultima_posicao = db.session.query(db.func.max(Colaborador.posicao_fila)).scalar() or 0
        colaborador.posicao_fila = ultima_posicao + 1
        
        # Marca solicitação como pendente novamente
        solicitacao.status = 'pendente'
        
        db.session.commit()
        
        # Distribui para o próximo colaborador
        return GerenciadorFila.distribuir_solicitacao(solicitacao_id)
    
    @staticmethod
    def processar_timeout(colaborador_id, solicitacao_id):
        """
        Processa timeout de atendimento (20 minutos sem resposta)
        Passa automaticamente para o próximo colaborador
        """
        colaborador = Colaborador.query.get(colaborador_id)
        solicitacao = Solicitacao.query.get(solicitacao_id)
        
        if not colaborador or not solicitacao:
            return None
        
        # Busca o atendimento atual
        atendimento = Atendimento.query.filter_by(
            colaborador_id=colaborador_id,
            solicitacao_id=solicitacao_id,
            status='em_atendimento'
        ).first()
        
        if not atendimento:
            return None
        
        # Verifica se realmente passou do timeout
        timeout_minutos = current_app.config.get('TIMEOUT_MINUTOS', 20)
        tempo_decorrido = datetime.utcnow() - atendimento.inicio
        
        if tempo_decorrido < timedelta(minutes=timeout_minutos):
            return None  # Ainda não deu timeout
        
        # Marca como timeout
        atendimento.finalizar(foi_timeout=True)
        
        # Retorna colaborador ao final da fila
        colaborador.finalizar_atendimento()
        ultima_posicao = db.session.query(db.func.max(Colaborador.posicao_fila)).scalar() or 0
        colaborador.posicao_fila = ultima_posicao + 1
        
        # Marca solicitação como pendente novamente
        solicitacao.status = 'pendente'
        
        db.session.commit()
        
        # Distribui para o próximo colaborador
        return GerenciadorFila.distribuir_solicitacao(solicitacao_id)
    
    @staticmethod
    def verificar_timeouts():
        """
        Verifica todos os atendimentos em andamento e processa timeouts
        Deve ser chamado periodicamente (ex: a cada minuto)
        """
        timeout_minutos = current_app.config.get('TIMEOUT_MINUTOS', 20)
        tempo_limite = datetime.utcnow() - timedelta(minutes=timeout_minutos)
        
        # Busca atendimentos que passaram do tempo
        atendimentos_timeout = Atendimento.query.filter(
            Atendimento.status == 'em_atendimento',
            Atendimento.inicio <= tempo_limite
        ).all()
        
        resultados = []
        for atendimento in atendimentos_timeout:
            proximo = GerenciadorFila.processar_timeout(
                atendimento.colaborador_id,
                atendimento.solicitacao_id
            )
            if proximo:
                resultados.append({
                    'solicitacao_id': atendimento.solicitacao_id,
                    'colaborador_anterior': atendimento.colaborador_id,
                    'proximo_colaborador': proximo.id
                })
        
        return resultados
    
    @staticmethod
    def obter_estatisticas_gerais():
        """Retorna estatísticas gerais do sistema"""
        total_colaboradores = Colaborador.query.count()
        colaboradores_disponiveis = Colaborador.query.filter_by(esta_disponivel=True).count()
        colaboradores_atendendo = Colaborador.query.filter_by(esta_em_atendimento=True).count()
        
        total_solicitacoes = Solicitacao.query.count()
        solicitacoes_pendentes = Solicitacao.query.filter_by(status='pendente').count()
        solicitacoes_em_atendimento = Solicitacao.query.filter_by(status='em_atendimento').count()
        solicitacoes_concluidas = Solicitacao.query.filter_by(status='concluido').count()
        
        total_atendimentos = Atendimento.query.count()
        atendimentos_concluidos = Atendimento.query.filter_by(status='concluido').count()
        atendimentos_pulados = Atendimento.query.filter_by(foi_pulado=True).count()
        atendimentos_timeout = Atendimento.query.filter_by(foi_timeout=True).count()
        
        return {
            'colaboradores': {
                'total': total_colaboradores,
                'disponiveis': colaboradores_disponiveis,
                'atendendo': colaboradores_atendendo
            },
            'solicitacoes': {
                'total': total_solicitacoes,
                'pendentes': solicitacoes_pendentes,
                'em_atendimento': solicitacoes_em_atendimento,
                'concluidas': solicitacoes_concluidas
            },
            'atendimentos': {
                'total': total_atendimentos,
                'concluidos': atendimentos_concluidos,
                'pulados': atendimentos_pulados,
                'timeout': atendimentos_timeout
            }
        }
