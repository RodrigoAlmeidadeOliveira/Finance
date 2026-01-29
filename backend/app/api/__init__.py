"""
Registro central de blueprints da API.
"""
from flask import Flask

from .auth import auth_bp
from .imports import imports_bp
from .catalog import catalog_bp
from .reports import reports_bp
from .planning import planning_bp
from .ml import ml_bp
from .investments import investments_bp
from .ai import ai_bp
from .training import training_bp
from .transactions import transactions_bp
from .backup import backup_bp


def register_blueprints(app: Flask) -> None:
    """
    Registra todos os blueprints da aplicação.
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
    app.register_blueprint(transactions_bp)
    app.register_blueprint(backup_bp)


__all__ = ["register_blueprints"]
