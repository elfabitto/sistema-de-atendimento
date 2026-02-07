"""
Script para inicializar o banco de dados com dados de exemplo
"""
from app import create_app
from app.models import db, Colaborador, Solicitacao

def init_database():
    """Inicializa o banco de dados e cria dados de exemplo"""
    app = create_app()
    
    with app.app_context():
        print('🔧 Criando tabelas do banco de dados...')
        db.create_all()
        print('✅ Tabelas criadas com sucesso!')
        
        # Verifica se já existem colaboradores
        if Colaborador.query.count() > 0:
            print('⚠️  Banco de dados já contém dados.')
            resposta = input('Deseja recriar os dados de exemplo? (s/n): ')
            if resposta.lower() != 's':
                print('❌ Operação cancelada.')
                return
            
            # Remove dados existentes
            print('🗑️  Removendo dados existentes...')
            db.drop_all()
            db.create_all()
        
        print('\n👥 Criando colaboradores de exemplo...')
        
        # Cria colaborador admin
        admin = Colaborador(
            nome='Administrador',
            email='admin@empresa.com'
        )
        admin.set_senha('admin123')
        db.session.add(admin)
        print('   ✓ Admin criado')
        
        # Cria colaboradores de exemplo
        colaboradores_exemplo = [
            {'nome': 'João Silva', 'email': 'joao@empresa.com', 'senha': 'senha123'},
            {'nome': 'Maria Santos', 'email': 'maria@empresa.com', 'senha': 'senha123'},
            {'nome': 'Pedro Oliveira', 'email': 'pedro@empresa.com', 'senha': 'senha123'},
            {'nome': 'Ana Costa', 'email': 'ana@empresa.com', 'senha': 'senha123'},
        ]
        
        for dados in colaboradores_exemplo:
            colaborador = Colaborador(
                nome=dados['nome'],
                email=dados['email']
            )
            colaborador.set_senha(dados['senha'])
            db.session.add(colaborador)
            print(f'   ✓ {dados["nome"]} criado')
        
        # Commit dos colaboradores
        db.session.commit()
        
        print('\n📋 Criando solicitações de exemplo...')
        
        # Cria algumas solicitações de exemplo
        solicitacoes_exemplo = [
            {
                'descricao': 'Cliente perguntando sobre horário de funcionamento',
                'cliente_nome': 'Carlos Mendes',
                'cliente_telefone': '(11) 98765-4321'
            },
            {
                'descricao': 'Dúvida sobre produto X - preço e disponibilidade',
                'cliente_nome': 'Fernanda Lima',
                'cliente_telefone': '(11) 97654-3210'
            },
            {
                'descricao': 'Reclamação sobre entrega atrasada',
                'cliente_nome': 'Roberto Alves',
                'cliente_telefone': '(11) 96543-2109'
            },
        ]
        
        for dados in solicitacoes_exemplo:
            solicitacao = Solicitacao(
                descricao=dados['descricao'],
                cliente_nome=dados['cliente_nome'],
                cliente_telefone=dados['cliente_telefone'],
                status='pendente'
            )
            db.session.add(solicitacao)
            print(f'   ✓ Solicitação criada: {dados["descricao"][:50]}...')
        
        # Commit das solicitações
        db.session.commit()
        
        print('\n' + '='*60)
        print('✅ Banco de dados inicializado com sucesso!')
        print('='*60)
        
        print('\n👤 CREDENCIAIS DE ACESSO:')
        print('\n📌 Administrador:')
        print('   Email: admin@empresa.com')
        print('   Senha: admin123')
        
        print('\n📌 Colaboradores de exemplo:')
        for dados in colaboradores_exemplo:
            print(f'   Email: {dados["email"]}')
            print(f'   Senha: {dados["senha"]}')
            print()
        
        print('⚠️  IMPORTANTE: Altere essas senhas em produção!')
        print('\n🚀 Execute "python run.py" para iniciar o servidor')
        print('='*60)


if __name__ == '__main__':
    init_database()
