"""
Modelo de tipos de investimento.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, Integer, String, UniqueConstraint

from .base import Base


class InvestmentType(Base):
    """Tipos de produtos de investimento (CDB, ETF, etc.)."""

    __tablename__ = "investment_types"
    __table_args__ = (
        UniqueConstraint("name", name="uq_investment_type_name"),
    )

    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    classification = Column(String(50), nullable=True)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "classification": self.classification,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def apply_updates(
        self,
        *,
        name: Optional[str] = None,
        classification: Optional[str] = None,
        description: Optional[str] = None,
    ) -> None:
        if name is not None:
            self.name = name
        if classification is not None:
            self.classification = classification
        if description is not None:
            self.description = description
