"""
Arquivo principal para executar a aplicação
"""
import os
import atexit
from app import create_app, socketio, shutdown_scheduler

# Cria a aplicação
app = create_app()

# Registra função para desligar o scheduler ao encerrar
atexit.register(shutdown_scheduler)

if __name__ == '__main__':
    # Obtém configurações de host e porta
    host = app.config.get('HOST', '0.0.0.0')
    port = app.config.get('PORT', 5000)
    debug = app.config.get('DEBUG', False)
    
    print(f"""
    ╔═══════════════════════════════════════════════════════════╗
    ║   Sistema de Gerenciamento de Fila de Atendimento        ║
    ╚═══════════════════════════════════════════════════════════╝
    
    🚀 Servidor iniciado em: http://{host}:{port}
    🔧 Modo: {'Desenvolvimento' if debug else 'Produção'}
    ⏱️  Timeout de atendimento: {app.config.get('TIMEOUT_MINUTOS', 20)} minutos
    
    📝 Para acessar:
       - Abra seu navegador em http://localhost:{port}
       - Use Ctrl+C para encerrar o servidor
    
    ═══════════════════════════════════════════════════════════
    """)
    
    # Executa a aplicação com SocketIO
    socketio.run(
        app,
        host=host,
        port=port,
        debug=debug,
        use_reloader=debug
    )
