"""
Infraestrutura de conexão com banco via SQLAlchemy.
"""
from __future__ import annotations

from contextlib import contextmanager
from typing import Dict, Generator, Optional

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import scoped_session, sessionmaker, Session

from .config import Config
from .models.base import Base

_engine: Optional[Engine] = None
_session_factory: Optional[scoped_session] = None


def init_engine(
    database_url: Optional[str] = None,
    echo: bool = False,
    engine_options: Optional[Dict] = None,
) -> Engine:
    """
    Inicializa o engine SQLAlchemy e sessão compartilhada.

    Args:
        database_url: URL de conexão do banco
        echo: Flag para logar SQL

    Returns:
        Engine inicializado
    """
    global _engine, _session_factory

    db_url = database_url or Config.SQLALCHEMY_DATABASE_URI
    options = {"future": True, **(engine_options or {})}
    _engine = create_engine(db_url, echo=echo, **options)
    _session_factory = scoped_session(
        sessionmaker(bind=_engine, autocommit=False, autoflush=False)
    )
    Base.metadata.bind = _engine
    return _engine


def init_app(app) -> Engine:
    """
    Inicializa engine a partir da configuração Flask e registra teardown.
    """
    engine = init_engine(
        database_url=app.config["SQLALCHEMY_DATABASE_URI"],
        echo=app.config.get("SQLALCHEMY_ECHO", False),
        engine_options=app.config.get("SQLALCHEMY_ENGINE_OPTIONS", {}),
    )
    app.teardown_appcontext(remove_session)
    return engine


def get_engine() -> Engine:
    """
    Retorna engine atual ou lança erro caso ainda não tenha sido inicializado.
    """
    if _engine is None:
        raise RuntimeError("Database engine not initialized. Call init_engine() first.")
    return _engine


def get_session() -> Session:
    """
    Obtém uma sessão ligada ao scoped_session global.
    """
    if _session_factory is None:
        raise RuntimeError("Session factory not initialized. Call init_engine() first.")
    return _session_factory()


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    """
    Context manager para sessões com commit/rollback automáticos.
    """
    session = get_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def remove_session(exception=None):
    """
    Remove sessão associada ao contexto Flask atual.
    """
    if _session_factory is not None:
        _session_factory.remove()
