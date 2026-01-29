"""
Configurações da aplicação Flask
"""
import os
from datetime import timedelta
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()


class Config:
    """Configuração base"""

    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = False
    TESTING = False

    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'postgresql://planner_user:senha123@localhost:5432/planner_financeiro'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
    }

    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        seconds=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600))
    )
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(
        seconds=int(os.getenv('JWT_REFRESH_TOKEN_EXPIRES', 2592000))
    )
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'

    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
    CORS_SUPPORTS_CREDENTIALS = True

    # Upload
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', '/tmp/planner_uploads')
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB
    ALLOWED_EXTENSIONS = {'ofx', 'csv'}

    # ML Model
    ML_MODEL_PATH = os.getenv('ML_MODEL_PATH', 'app/ml/models/category_classifier.pkl')
    ML_MODELS_FOLDER = os.getenv('ML_MODELS_FOLDER', 'app/ml/models')

    # OpenAI Integration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
    OPENAI_MAX_TOKENS = int(os.getenv('OPENAI_MAX_TOKENS', 1000))
    AUTO_RETRAIN_THRESHOLD = int(os.getenv('AUTO_RETRAIN_THRESHOLD', 100))

    # Rate Limiting
    RATELIMIT_STORAGE_URL = 'memory://'  # Usar Redis em produção
    RATELIMIT_DEFAULT = "100 per hour"
    RATELIMIT_AI_ENDPOINT = "20 per hour"  # Limite mais restrito para IA

    # Bcrypt
    BCRYPT_LOG_ROUNDS = 12

    # Security Headers
    SESSION_COOKIE_SECURE = False  # True em produção com HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'


class DevelopmentConfig(Config):
    """Configuração de desenvolvimento"""

    DEBUG = True
    SQLALCHEMY_ECHO = True
    SESSION_COOKIE_SECURE = False

    # Permitir múltiplas origens em desenvolvimento
    CORS_ORIGINS = ['http://localhost:3000', 'http://localhost:5001', 'http://127.0.0.1:5001']


class ProductionConfig(Config):
    """Configuração de produção"""

    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True
    RATELIMIT_STORAGE_URL = os.getenv('REDIS_URL', 'memory://')


class TestingConfig(Config):
    """Configuração de testes"""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


# Mapeamento de ambientes
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
