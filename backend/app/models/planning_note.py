"""
Notas gerais de planejamento financeiro.
"""
from __future__ import annotations

from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, Text

from .base import Base


class PlanningNote(Base):
    __tablename__ = "planning_notes"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, default=1)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "content": self.content,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
