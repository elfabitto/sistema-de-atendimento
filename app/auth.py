"""
Sistema de autenticação de colaboradores
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models import db, Colaborador

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    # Se já está logado, redireciona para o dashboard
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        lembrar = request.form.get('lembrar', False) == 'on'
        
        # Validação básica
        if not email or not senha:
            flash('Por favor, preencha todos os campos.', 'error')
            return render_template('login.html')
        
        # Busca o colaborador
        colaborador = Colaborador.query.filter_by(email=email).first()
        
        # Verifica credenciais
        if colaborador and colaborador.verificar_senha(senha):
            login_user(colaborador, remember=lembrar)
            
            # Redireciona para a página solicitada ou dashboard
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('main.dashboard'))
        else:
            flash('Email ou senha incorretos.', 'error')
    
    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """Faz logout do colaborador"""
    # Se estiver na fila, remove antes de fazer logout
    if current_user.esta_disponivel:
        from app.fila import GerenciadorFila
        GerenciadorFila.remover_colaborador(current_user.id)
    
    logout_user()
    flash('Você saiu do sistema com sucesso.', 'success')
    return redirect(url_for('auth.login'))


@auth_bp.route('/registro', methods=['GET', 'POST'])
def registro():
    """
    Página de registro de novos colaboradores
    (Pode ser desabilitada em produção para permitir apenas registro por admin)
    """
    # Se já está logado, redireciona para o dashboard
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')
        confirmar_senha = request.form.get('confirmar_senha')
        
        # Validações
        if not all([nome, email, senha, confirmar_senha]):
            flash('Por favor, preencha todos os campos.', 'error')
            return render_template('registro.html')
        
        if senha != confirmar_senha:
            flash('As senhas não coincidem.', 'error')
            return render_template('registro.html')
        
        if len(senha) < 6:
            flash('A senha deve ter pelo menos 6 caracteres.', 'error')
            return render_template('registro.html')
        
        # Verifica se o email já existe
        if Colaborador.query.filter_by(email=email).first():
            flash('Este email já está cadastrado.', 'error')
            return render_template('registro.html')
        
        # Cria o novo colaborador
        novo_colaborador = Colaborador(
            nome=nome,
            email=email
        )
        novo_colaborador.set_senha(senha)
        
        db.session.add(novo_colaborador)
        db.session.commit()
        
        flash('Cadastro realizado com sucesso! Faça login para continuar.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('registro.html')


@auth_bp.route('/perfil')
@login_required
def perfil():
    """Página de perfil do colaborador"""
    estatisticas = current_user.get_estatisticas()
    return render_template('perfil.html', estatisticas=estatisticas)


@auth_bp.route('/alterar-senha', methods=['GET', 'POST'])
@login_required
def alterar_senha():
    """Permite ao colaborador alterar sua senha"""
    if request.method == 'POST':
        senha_atual = request.form.get('senha_atual')
        nova_senha = request.form.get('nova_senha')
        confirmar_senha = request.form.get('confirmar_senha')
        
        # Validações
        if not all([senha_atual, nova_senha, confirmar_senha]):
            flash('Por favor, preencha todos os campos.', 'error')
            return render_template('alterar_senha.html')
        
        if not current_user.verificar_senha(senha_atual):
            flash('Senha atual incorreta.', 'error')
            return render_template('alterar_senha.html')
        
        if nova_senha != confirmar_senha:
            flash('As senhas não coincidem.', 'error')
            return render_template('alterar_senha.html')
        
        if len(nova_senha) < 6:
            flash('A nova senha deve ter pelo menos 6 caracteres.', 'error')
            return render_template('alterar_senha.html')
        
        # Atualiza a senha
        current_user.set_senha(nova_senha)
        db.session.commit()
        
        flash('Senha alterada com sucesso!', 'success')
        return redirect(url_for('auth.perfil'))
    
    return render_template('alterar_senha.html')
