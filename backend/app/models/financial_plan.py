"""
Modelo de planos financeiros (metas e aportes recorrentes).
"""
from __future__ import annotations

from datetime import datetime, date
from typing import Optional

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)

from .base import Base


class FinancialPlan(Base):
    """Plano financeiro com meta e progresso."""

    __tablename__ = "financial_plans"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, default=1)
    name = Column(String(200), nullable=False)
    goal_amount = Column(Float, nullable=False)
    current_balance = Column(Float, nullable=False, default=0.0)
    monthly_contribution = Column(Float, nullable=False, default=0.0)
    institution_id = Column(Integer, ForeignKey("institutions.id"), nullable=True)
    partition = Column(String(50), nullable=True)
    target_date = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "goal_amount": self.goal_amount,
            "current_balance": self.current_balance,
            "monthly_contribution": self.monthly_contribution,
            "institution_id": self.institution_id,
            "partition": self.partition,
            "target_date": self.target_date.isoformat() if self.target_date else None,
            "is_active": self.is_active,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def apply_updates(
        self,
        *,
        name: Optional[str] = None,
        goal_amount: Optional[float] = None,
        current_balance: Optional[float] = None,
        monthly_contribution: Optional[float] = None,
        institution_id: Optional[int] = None,
        partition: Optional[str] = None,
        target_date: Optional[date] = None,
        is_active: Optional[bool] = None,
        notes: Optional[str] = None,
    ) -> None:
        if name is not None:
            self.name = name
        if goal_amount is not None:
            self.goal_amount = goal_amount
        if current_balance is not None:
            self.current_balance = current_balance
        if monthly_contribution is not None:
            self.monthly_contribution = monthly_contribution
        if institution_id is not None:
            self.institution_id = institution_id
        if partition is not None:
            self.partition = partition
        if target_date is not None:
            self.target_date = target_date
        if is_active is not None:
            self.is_active = is_active
        if notes is not None:
            self.notes = notes
