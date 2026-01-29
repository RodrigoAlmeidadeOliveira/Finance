"""
Modelo para jobs de treinamento de modelos ML.
"""
from __future__ import annotations

import enum
from datetime import datetime
from typing import TYPE_CHECKING, Dict

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship

from .base import Base

if TYPE_CHECKING:
    from .user import User


class TrainingJobStatus(enum.Enum):
    """Status de um job de treinamento"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class TrainingJobSource(enum.Enum):
    """Origem dos dados de treinamento"""
    CSV_UPLOAD = "csv_upload"
    AUTO_RETRAIN = "auto_retrain"


class TrainingJob(Base):
    """
    Representa um job de treinamento de modelo ML.

    Atributos:
        id: ID único do job
        user_id: Usuário que iniciou o treinamento
        status: Status atual do job
        source: Origem dos dados (CSV ou auto-retrain)
        csv_path: Caminho do CSV uploadado (se source=CSV_UPLOAD)
        model_version: Versão/timestamp do modelo gerado
        metrics: JSON com métricas de treinamento (accuracy, f1, etc)
        created_at: Data de criação do job
        completed_at: Data de conclusão (se completado)
        error_message: Mensagem de erro (se falhou)
    """
    __tablename__ = "training_jobs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(Enum(TrainingJobStatus), nullable=False, default=TrainingJobStatus.PENDING)
    source = Column(Enum(TrainingJobSource), nullable=False)
    csv_path = Column(String(500), nullable=True)
    model_version = Column(String(100), nullable=True)
    metrics = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)

    # Relacionamentos
    user = relationship("User", back_populates="training_jobs")

    def to_dict(self) -> Dict:
        """Converte para dicionário"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "status": self.status.value if self.status else None,
            "source": self.source.value if self.source else None,
            "csv_path": self.csv_path,
            "model_version": self.model_version,
            "metrics": self.metrics,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error_message": self.error_message,
        }
