"""
Modelo de categorias e subcategorias.
"""
from __future__ import annotations

import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from .base import Base


class CategoryType(enum.Enum):
    """Tipo da categoria (receita ou despesa)."""

    INCOME = "income"
    EXPENSE = "expense"


class Category(Base):
    """
    Categoria de transações. Subcategorias são modeladas via parent_id.
    """

    __tablename__ = "categories"
    __table_args__ = (
        UniqueConstraint("user_id", "name", "parent_id", name="uq_category_per_parent"),
    )

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, default=1)
    name = Column(String(100), nullable=False)
    type = Column(Enum(CategoryType), nullable=False)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    color = Column(String(20), nullable=True)
    icon = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    parent = relationship("Category", remote_side=[id], backref="children")

    def to_dict(self, include_children: bool = False) -> dict:
        data = {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "type": self.type.value if self.type else None,
            "parent_id": self.parent_id,
            "color": self.color,
            "icon": self.icon,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

        if include_children:
            data["children"] = [child.to_dict(False) for child in self.children]

        return data

    def apply_updates(
        self,
        *,
        name: Optional[str] = None,
        category_type: Optional[CategoryType] = None,
        parent: Optional["Category"] = None,
        color: Optional[str] = None,
        icon: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> None:
        if name is not None:
            self.name = name
        if category_type is not None:
            self.type = category_type
        if parent is not None:
            self.parent = parent
        if color is not None:
            self.color = color
        if icon is not None:
            self.icon = icon
        if is_active is not None:
            self.is_active = is_active
