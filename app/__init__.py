"""
Inicialização da aplicação Flask
"""
from flask import Flask
from flask_socketio import SocketIO
from flask_login import LoginManager
from flask_migrate import Migrate
from apscheduler.schedulers.background import BackgroundScheduler
from config import get_config
from app.models import db, Colaborador
from app.fila import GerenciadorFila

# Inicializa extensões
socketio = SocketIO()
login_manager = LoginManager()
migrate = Migrate()
scheduler = BackgroundScheduler()


def create_app():
    """Factory para criar a aplicação Flask"""
    app = Flask(__name__)
    
    # Carrega configurações
    app.config.from_object(get_config())
    
    # Inicializa extensões com a app
    db.init_app(app)
    socketio.init_app(app, 
                     async_mode=app.config['SOCKETIO_ASYNC_MODE'],
                     cors_allowed_origins=app.config['SOCKETIO_CORS_ALLOWED_ORIGINS'])
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    # Configurações do Flask-Login
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        """Carrega o usuário pelo ID"""
        return Colaborador.query.get(int(user_id))
    
    # Registra blueprints
    from app.auth import auth_bp
    from app.routes import main_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    
    # Registra eventos SocketIO
    from app.socket_events import register_socket_events
    register_socket_events(socketio)
    
    # Configura agendador de tarefas
    def verificar_timeouts_job():
        """Job para verificar timeouts periodicamente"""
        with app.app_context():
            try:
                resultados = GerenciadorFila.verificar_timeouts()
                if resultados:
                    print(f'Timeouts processados: {len(resultados)}')
                    # Notifica via SocketIO sobre os timeouts
                    for resultado in resultados:
                        socketio.emit('timeout_processado', resultado, 
                                    room=f'colaborador_{resultado["proximo_colaborador"]}')
            except Exception as e:
                print(f'Erro ao verificar timeouts: {e}')
    
    # Agenda verificação de timeouts a cada minuto
    if not scheduler.running:
        scheduler.add_job(
            func=verificar_timeouts_job,
            trigger='interval',
            minutes=1,
            id='verificar_timeouts',
            replace_existing=True
        )
        scheduler.start()
    
    # Context processor para disponibilizar variáveis em todos os templates
    @app.context_processor
    def inject_globals():
        """Injeta variáveis globais nos templates"""
        return {
            'app_name': 'Sistema de Fila de Atendimento',
            'timeout_minutos': app.config.get('TIMEOUT_MINUTOS', 20)
        }
    
    # Tratamento de erros
    @app.errorhandler(404)
    def not_found_error(error):
        """Página de erro 404"""
        from flask import render_template
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Página de erro 500"""
        from flask import render_template
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    # Comando CLI para inicializar o banco de dados
    @app.cli.command()
    def init_db():
        """Inicializa o banco de dados"""
        db.create_all()
        print('Banco de dados inicializado!')
    
    # Comando CLI para criar usuário admin
    @app.cli.command()
    def create_admin():
        """Cria um usuário administrador"""
        admin = Colaborador.query.filter_by(email='admin@empresa.com').first()
        if admin:
            print('Usuário admin já existe!')
            return
        
        admin = Colaborador(
            nome='Administrador',
            email='admin@empresa.com'
        )
        admin.set_senha('admin123')
        
        db.session.add(admin)
        db.session.commit()
        
        print('Usuário admin criado com sucesso!')
        print('Email: admin@empresa.com')
        print('Senha: admin123')
        print('IMPORTANTE: Altere a senha em produção!')
    
    return app


def shutdown_scheduler():
    """Desliga o agendador ao encerrar a aplicação"""
    if scheduler.running:
        scheduler.shutdown()
