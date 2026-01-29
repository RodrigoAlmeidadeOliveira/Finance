"""
Modelo de investimentos (carteira) e proventos.
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
from sqlalchemy.orm import relationship

from .base import Base


class Investment(Base):
    """Investimento cadastrado na carteira."""

    __tablename__ = "investments"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, default=1)
    name = Column(String(200), nullable=False)
    institution_id = Column(Integer, ForeignKey("institutions.id"), nullable=True)
    investment_type_id = Column(Integer, ForeignKey("investment_types.id"), nullable=True)
    classification = Column(String(50), nullable=True)  # renda_fixa / renda_variavel
    amount_invested = Column(Float, nullable=False, default=0.0)
    current_value = Column(Float, nullable=False, default=0.0)
    applied_at = Column(Date, nullable=True)
    maturity_date = Column(Date, nullable=True)
    profitability_rate = Column(Float, nullable=True)  # % a.a ou referencia
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    dividends = relationship("Dividend", back_populates="investment", cascade="all, delete-orphan")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "institution_id": self.institution_id,
            "investment_type_id": self.investment_type_id,
            "classification": self.classification,
            "amount_invested": self.amount_invested,
            "current_value": self.current_value,
            "applied_at": self.applied_at.isoformat() if self.applied_at else None,
            "maturity_date": self.maturity_date.isoformat() if self.maturity_date else None,
            "profitability_rate": self.profitability_rate,
            "notes": self.notes,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def apply_updates(
        self,
        *,
        name: Optional[str] = None,
        institution_id: Optional[int] = None,
        investment_type_id: Optional[int] = None,
        classification: Optional[str] = None,
        amount_invested: Optional[float] = None,
        current_value: Optional[float] = None,
        applied_at: Optional[date] = None,
        maturity_date: Optional[date] = None,
        profitability_rate: Optional[float] = None,
        notes: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> None:
        if name is not None:
            self.name = name
        if institution_id is not None:
            self.institution_id = institution_id
        if investment_type_id is not None:
            self.investment_type_id = investment_type_id
        if classification is not None:
            self.classification = classification
        if amount_invested is not None:
            self.amount_invested = amount_invested
        if current_value is not None:
            self.current_value = current_value
        if applied_at is not None:
            self.applied_at = applied_at
        if maturity_date is not None:
            self.maturity_date = maturity_date
        if profitability_rate is not None:
            self.profitability_rate = profitability_rate
        if notes is not None:
            self.notes = notes
        if is_active is not None:
            self.is_active = is_active


class Dividend(Base):
    """Proventos recebidos de um investimento."""

    __tablename__ = "dividends"

    id = Column(Integer, primary_key=True)
    investment_id = Column(Integer, ForeignKey("investments.id"), nullable=False)
    user_id = Column(Integer, nullable=False, default=1)
    description = Column(String(200), nullable=True)
    amount = Column(Float, nullable=False, default=0.0)
    received_at = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    investment = relationship("Investment", back_populates="dividends")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "investment_id": self.investment_id,
            "user_id": self.user_id,
            "description": self.description,
            "amount": self.amount,
            "received_at": self.received_at.isoformat() if self.received_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
