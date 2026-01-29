"""
Modelo de cartões de crédito.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from .base import Base


class CreditCard(Base):
    """Cartão de crédito vinculado a uma instituição."""

    __tablename__ = "credit_cards"
    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_credit_card_per_user"),
    )

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, default=1)
    institution_id = Column(Integer, ForeignKey("institutions.id"), nullable=False)
    name = Column(String(120), nullable=False)
    brand = Column(String(50), nullable=True)
    last_four_digits = Column(String(4), nullable=True)
    closing_day = Column(Integer, nullable=True)
    due_day = Column(Integer, nullable=True)
    limit_amount = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    institution = relationship("Institution", back_populates="credit_cards")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "institution_id": self.institution_id,
            "name": self.name,
            "brand": self.brand,
            "last_four_digits": self.last_four_digits,
            "closing_day": self.closing_day,
            "due_day": self.due_day,
            "limit_amount": self.limit_amount,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def apply_updates(
        self,
        *,
        name: Optional[str] = None,
        brand: Optional[str] = None,
        last_four_digits: Optional[str] = None,
        closing_day: Optional[int] = None,
        due_day: Optional[int] = None,
        limit_amount: Optional[float] = None,
        is_active: Optional[bool] = None,
        institution_id: Optional[int] = None,
    ) -> None:
        if name is not None:
            self.name = name
        if brand is not None:
            self.brand = brand
        if last_four_digits is not None:
            self.last_four_digits = last_four_digits
        if closing_day is not None:
            self.closing_day = closing_day
        if due_day is not None:
            self.due_day = due_day
        if limit_amount is not None:
            self.limit_amount = limit_amount
        if is_active is not None:
            self.is_active = is_active
        if institution_id is not None:
            self.institution_id = institution_id
