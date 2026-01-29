"""
Planejamento recorrente por categoria (período definido).
"""
from __future__ import annotations

from datetime import datetime, date
from typing import Optional

from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, Integer

from .base import Base


class CategoryRecurringPlan(Base):
    __tablename__ = "category_recurring_plans"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, default=1)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    amount = Column(Float, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "category_id": self.category_id,
            "amount": self.amount,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
