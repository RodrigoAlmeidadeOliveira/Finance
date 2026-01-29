"""
Aplicação principal Flask - Planner Financeiro
"""
import os
from flask import Flask, send_file, jsonify
from flask_cors import CORS

from app.config import config
from app.database import init_app as init_database
from app.models import Base
from app.services import AuthService, ImportService
from app.ml import TransactionPredictor
from app.api.auth import auth_bp
from app.api.imports import imports_bp
from app.api.catalog import catalog_bp
from app.api.reports import reports_bp
from app.api.planning import planning_bp
from app.api.ml import ml_bp
from app.api.investments import investments_bp
from app.api.ai import ai_bp
from app.api.training import training_bp


def create_app(config_name='development'):
    """
    Factory function para criar a aplicação Flask.

    Args:
        config_name: Nome da configuração ('development', 'production', 'testing')

    Returns:
        Aplicação Flask configurada
    """
    app = Flask(__name__)

    # Carregar configuração
    app.config.from_object(config[config_name])

    # Inicializar extensões
    init_extensions(app)

    # Registrar Blueprints
    register_blueprints(app)

    # Criar tabelas do banco de dados
    with app.app_context():
        Base.metadata.create_all(bind=app.extensions['db_engine'])

    return app


def init_extensions(app):
    """
    Inicializa extensões e serviços da aplicação.

    Args:
        app: Instância do Flask
    """
    # CORS
    CORS(app,
         origins=app.config['CORS_ORIGINS'],
         supports_credentials=app.config['CORS_SUPPORTS_CREDENTIALS'])

    # Database
    db_engine = init_database(app)
    app.extensions['db_engine'] = db_engine

    # ML Predictor
    model_path = app.config['ML_MODEL_PATH']
    if os.path.exists(model_path):
        predictor = TransactionPredictor(model_path)
        app.extensions['predictor'] = predictor
        app.logger.info(f"✅ ML Model loaded from {model_path}")
    else:
        app.logger.warning(f"⚠️  ML Model not found at {model_path}")
        app.extensions['predictor'] = None

    # Auth Service
    auth_service = AuthService(
        jwt_secret=app.config['JWT_SECRET_KEY'],
        access_token_expires=int(app.config['JWT_ACCESS_TOKEN_EXPIRES'].total_seconds()),
        refresh_token_expires=int(app.config['JWT_REFRESH_TOKEN_EXPIRES'].total_seconds())
    )
    app.extensions['auth_service'] = auth_service

    # Import Service (somente se o predictor estiver disponível)
    if app.extensions['predictor']:
        from app.database import get_session
        import_service = ImportService(
            session_factory=get_session,
            predictor=app.extensions['predictor'],
            upload_folder=app.config['UPLOAD_FOLDER']
        )
        app.extensions['import_service'] = import_service


def register_blueprints(app):
    """
    Registra os Blueprints da API.

    Args:
        app: Instância do Flask
    """
    app.register_blueprint(auth_bp)
    app.register_blueprint(imports_bp)
    app.register_blueprint(catalog_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(planning_bp)
    app.register_blueprint(ml_bp)
    app.register_blueprint(investments_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(training_bp)

    # Endpoint de auto-login apenas para desenvolvimento
    @app.route('/api/auth/dev-login', methods=['GET', 'POST'])
    def dev_login():
        """
        Auto-login como admin em ambiente de desenvolvimento.
        Retorna tokens de autenticação para o usuário admin padrão.
        """
        if not app.config.get('DEBUG', False) and os.getenv('FLASK_ENV') != 'development':
            return jsonify({'error': 'Endpoint disponível apenas em desenvolvimento'}), 403

        from app.database import get_session
        from app.models import User

        session = get_session()
        try:
            # Buscar ou criar admin padrão
            admin = session.query(User).filter(User.email == 'admin@planner.com').first()

            if not admin:
                admin = User.create_user(
                    email='admin@planner.com',
                    password='admin123',
                    full_name='Administrador',
                    is_admin=True
                )
                session.add(admin)
                session.commit()
                app.logger.info("✅ Admin user created via dev-login")

            # Gerar tokens
            auth_service = app.extensions['auth_service']
            access_token = auth_service.generate_access_token(admin)
            refresh_token = auth_service.generate_refresh_token(admin)

            return jsonify({
                'user': admin.to_dict(),
                'access_token': access_token,
                'refresh_token': refresh_token,
                'token_type': 'Bearer',
                'expires_in': auth_service.access_token_expires,
                'message': 'Auto-login de desenvolvimento realizado'
            }), 200

        except Exception as e:
            session.rollback()
            app.logger.error(f"❌ Dev-login error: {str(e)}")
            return jsonify({'error': f'Erro no auto-login: {str(e)}'}), 500
        finally:
            session.close()

    # Rota raiz para servir o frontend
    @app.route('/')
    def index():
        """
        Serve a página principal do frontend.
        """
        frontend_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'frontend',
            'app.html'
        )
        if os.path.exists(frontend_path):
            return send_file(frontend_path)
        else:
            return jsonify({
                'message': 'Planner Financeiro API',
                'version': '1.0.0',
                'frontend': 'Abra o arquivo frontend/app.html no navegador',
                'docs': 'Acesse /api/auth e /api/imports para usar a API'
            }), 200


if __name__ == '__main__':
    # Obter configuração do ambiente
    env = os.getenv('FLASK_ENV', 'development')
    app = create_app(env)

    # Configurações do servidor
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', '1') == '1'

    print("=" * 80)
    print("🚀 PLANNER FINANCEIRO - BACKEND API")
    print("=" * 80)
    print(f"Ambiente: {env}")
    print(f"URL: http://{host}:{port}")
    print(f"Debug: {debug}")
    print(f"ML Model: {'✅ Loaded' if app.extensions.get('predictor') else '⚠️  Not loaded'}")

    if env == 'development':
        print("-" * 80)
        print("🔐 DEV LOGIN: GET /api/auth/dev-login")
        print("   Email: admin@planner.com | Senha: admin123")

    print("=" * 80)

    app.run(host=host, port=port, debug=debug)
