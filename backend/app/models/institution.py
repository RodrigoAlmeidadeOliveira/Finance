"""
Modelo de instituições financeiras.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from .base import Base


class Institution(Base):
    """
    Instituições financeiras (bancos/corretoras/contas).
    """

    __tablename__ = "institutions"
    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_institution_per_user"),
    )

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, default=1)
    name = Column(String(120), nullable=False)
    account_type = Column(String(50), nullable=False)
    partition = Column(String(50), nullable=True)
    initial_balance = Column(Float, default=0.0, nullable=False)
    current_balance = Column(Float, default=0.0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    credit_cards = relationship(
        "CreditCard",
        back_populates="institution",
        cascade="all, delete-orphan",
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "account_type": self.account_type,
            "partition": self.partition,
            "initial_balance": self.initial_balance,
            "current_balance": self.current_balance,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def apply_updates(
        self,
        *,
        name: Optional[str] = None,
        account_type: Optional[str] = None,
        partition: Optional[str] = None,
        initial_balance: Optional[float] = None,
        current_balance: Optional[float] = None,
        is_active: Optional[bool] = None,
    ) -> None:
        if name is not None:
            self.name = name
        if account_type is not None:
            self.account_type = account_type
        if partition is not None:
            self.partition = partition
        if initial_balance is not None:
            self.initial_balance = initial_balance
        if current_balance is not None:
            self.current_balance = current_balance
        if is_active is not None:
            self.is_active = is_active
