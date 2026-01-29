"""
Factory da aplicação Flask e inicialização de dependências globais.
"""
from __future__ import annotations

import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from .api import register_blueprints
from .config import config as app_config
from .database import init_app as init_db
from .ml import TransactionPredictor
from .services import AuthService


def create_app(config_name: str | None = None) -> Flask:
    """
    Cria e configura a aplicação Flask.
    """
    app = Flask(__name__)
    config_key = config_name or os.getenv("FLASK_CONFIG", "default")
    app.config.from_object(app_config[config_key])

    CORS(
        app,
        origins=app.config.get("CORS_ORIGINS", []),
        supports_credentials=app.config.get("CORS_SUPPORTS_CREDENTIALS", True),
    )
    JWTManager(app)
    Limiter(
        get_remote_address,
        app=app,
        default_limits=[app.config.get("RATELIMIT_DEFAULT", "100 per hour")],
    )

    # Banco de dados e recursos compartilhados
    init_db(app)
    model_path = app.config["ML_MODEL_PATH"]
    if os.path.exists(model_path):
        app.extensions["predictor"] = TransactionPredictor(model_path)
    else:
        app.logger.warning("ML model not found at %s. Predictor disabled.", model_path)
        app.extensions["predictor"] = None

    # Auth Service
    auth_service = AuthService(
        jwt_secret=app.config['JWT_SECRET_KEY'],
        access_token_expires=int(app.config['JWT_ACCESS_TOKEN_EXPIRES'].total_seconds()),
        refresh_token_expires=int(app.config['JWT_REFRESH_TOKEN_EXPIRES'].total_seconds())
    )
    app.extensions['auth_service'] = auth_service

    # Rotas
    register_blueprints(app)

    @app.get("/health")
    def healthcheck():
        return jsonify({"status": "ok"})

    return app


__all__ = ["create_app"]
