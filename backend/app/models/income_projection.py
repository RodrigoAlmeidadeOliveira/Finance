"""
Modelo de projeções de receita (fixas e extras).
"""
from __future__ import annotations

from datetime import datetime, date
from typing import Optional
from enum import Enum

from sqlalchemy import Boolean, Column, Date, DateTime, Enum as SAEnum, Float, Integer, String

from .base import Base


class IncomeProjectionType(str, Enum):
    FIXED = "fixed"
    EXTRA = "extra"


class IncomeProjection(Base):
    """Receitas previstas para períodos futuros ou recorrentes."""

    __tablename__ = "income_projections"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, default=1)
    description = Column(String(200), nullable=False)
    amount = Column(Float, nullable=False)
    expected_date = Column(Date, nullable=False)
    projection_type = Column(SAEnum(IncomeProjectionType), default=IncomeProjectionType.FIXED, nullable=False)
    received = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "description": self.description,
            "amount": self.amount,
            "expected_date": self.expected_date.isoformat() if self.expected_date else None,
            "projection_type": self.projection_type.value if self.projection_type else None,
            "received": self.received,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def apply_updates(
        self,
        *,
        description: Optional[str] = None,
        amount: Optional[float] = None,
        expected_date: Optional[date] = None,
        projection_type: Optional["IncomeProjectionType"] = None,
        received: Optional[bool] = None,
    ) -> None:
        if description is not None:
            self.description = description
        if amount is not None:
            self.amount = amount
        if expected_date is not None:
            self.expected_date = expected_date
        if projection_type is not None:
            self.projection_type = projection_type
        if received is not None:
            self.received = received
