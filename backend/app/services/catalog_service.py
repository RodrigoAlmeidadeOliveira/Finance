"""
Serviço para CRUD de cadastros base (categorias, instituições, cartões, tipos de investimento).
"""
from __future__ import annotations

from contextlib import contextmanager
from typing import Callable, Iterable, List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from ..models import (
    Category,
    CategoryType,
    CreditCard,
    Institution,
    InvestmentType,
)


class CatalogService:
    """
    Operações de CRUD para cadastros base usados pelos módulos financeiros.
    """

    def __init__(self, session_factory: Callable[[], Session]):
        self.session_factory = session_factory

    @contextmanager
    def _session_scope(self):
        session = self.session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    # --- Categorias ---
    def list_categories(
        self,
        *,
        category_type: Optional[str] = None,
        parent_id: Optional[int] = None,
        include_inactive: bool = False,
    ) -> List[dict]:
        session = self.session_factory()
        try:
            query = session.query(Category)

            parsed_type = self._parse_category_type(category_type) if category_type else None
            if parsed_type:
                query = query.filter(Category.type == parsed_type)

            if parent_id is not None:
                query = query.filter(Category.parent_id == parent_id)

            if not include_inactive:
                query = query.filter(Category.is_active.is_(True))

            categories = query.order_by(Category.name.asc()).all()
            return [c.to_dict() for c in categories]
        finally:
            session.close()

    def get_category(self, category_id: int) -> Optional[dict]:
        session = self.session_factory()
        try:
            category = session.get(Category, category_id)
            return category.to_dict(include_children=True) if category else None
        finally:
            session.close()

    def create_category(
        self,
        *,
        name: str,
        category_type: str,
        user_id: int = 1,
        parent_id: Optional[int] = None,
        color: Optional[str] = None,
        icon: Optional[str] = None,
    ) -> dict:
        clean_name = self._normalize_name(name)
        parsed_type = self._parse_category_type(category_type)
        if not parsed_type:
            raise ValueError("Tipo de categoria inválido. Use 'income' ou 'expense'.")

        with self._session_scope() as session:
            parent = None
            if parent_id is not None:
                parent = session.get(Category, parent_id)
                if not parent:
                    raise ValueError("Categoria pai não encontrada.")
                if parent.type != parsed_type:
                    raise ValueError("Subcategoria deve ter o mesmo tipo da categoria pai.")

            self._ensure_unique_category(session, user_id, clean_name, parent_id)

            category = Category(
                user_id=user_id,
                name=clean_name,
                type=parsed_type,
                parent=parent,
                color=color,
                icon=icon,
            )
            session.add(category)
            session.flush()
            return category.to_dict()

    def update_category(
        self,
        category_id: int,
        *,
        name: Optional[str] = None,
        category_type: Optional[str] = None,
        parent_id: Optional[int] = None,
        color: Optional[str] = None,
        icon: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> Optional[dict]:
        with self._session_scope() as session:
            category = session.get(Category, category_id)
            if not category:
                return None

            new_type = category.type
            if category_type is not None:
                parsed_type = self._parse_category_type(category_type)
                if not parsed_type:
                    raise ValueError("Tipo de categoria inválido. Use 'income' ou 'expense'.")
                new_type = parsed_type

            parent = category.parent
            if parent_id is not None:
                if parent_id == category.id:
                    raise ValueError("Categoria não pode ser pai de si mesma.")
                parent = session.get(Category, parent_id)
                if not parent:
                    raise ValueError("Categoria pai não encontrada.")
                if parent.type != new_type:
                    raise ValueError("Subcategoria deve ter o mesmo tipo da categoria pai.")

            new_name = self._normalize_name(name) if name is not None else category.name
            self._ensure_unique_category(session, category.user_id, new_name, parent.id if parent else None, exclude_id=category.id)

            if category.children and any(child.type != new_type for child in category.children):
                raise ValueError("Não é possível alterar tipo enquanto existir subcategoria com tipo diferente.")

            category.apply_updates(
                name=new_name if name is not None else None,
                category_type=new_type if category_type is not None else None,
                parent=parent if parent_id is not None else None,
                color=color,
                icon=icon,
                is_active=is_active,
            )
            session.flush()
            return category.to_dict()

    def delete_category(self, category_id: int) -> bool:
        with self._session_scope() as session:
            category = session.get(Category, category_id)
            if not category:
                return False
            if category.children:
                raise ValueError("Remova ou recoloque as subcategorias antes de excluir a categoria.")
            session.delete(category)
            return True

    # --- Instituições ---
    def list_institutions(self, *, include_inactive: bool = False) -> List[dict]:
        session = self.session_factory()
        try:
            query = session.query(Institution)
            if not include_inactive:
                query = query.filter(Institution.is_active.is_(True))
            items = query.order_by(Institution.name.asc()).all()
            return [inst.to_dict() for inst in items]
        finally:
            session.close()

    def create_institution(
        self,
        *,
        name: str,
        account_type: str,
        user_id: int = 1,
        partition: Optional[str] = None,
        initial_balance: float = 0.0,
        current_balance: Optional[float] = None,
    ) -> dict:
        clean_name = self._normalize_name(name)
        with self._session_scope() as session:
            self._ensure_unique_institution(session, user_id, clean_name)

            institution = Institution(
                user_id=user_id,
                name=clean_name,
                account_type=account_type,
                partition=partition,
                initial_balance=initial_balance,
                current_balance=current_balance if current_balance is not None else initial_balance,
            )
            session.add(institution)
            session.flush()
            return institution.to_dict()

    def update_institution(
        self,
        institution_id: int,
        *,
        name: Optional[str] = None,
        account_type: Optional[str] = None,
        partition: Optional[str] = None,
        initial_balance: Optional[float] = None,
        current_balance: Optional[float] = None,
        is_active: Optional[bool] = None,
    ) -> Optional[dict]:
        with self._session_scope() as session:
            institution = session.get(Institution, institution_id)
            if not institution:
                return None

            new_name = self._normalize_name(name) if name is not None else institution.name
            if name is not None:
                self._ensure_unique_institution(session, institution.user_id, new_name, exclude_id=institution.id)

            institution.apply_updates(
                name=new_name if name is not None else None,
                account_type=account_type,
                partition=partition,
                initial_balance=initial_balance,
                current_balance=current_balance,
                is_active=is_active,
            )
            session.flush()
            return institution.to_dict()

    def delete_institution(self, institution_id: int) -> bool:
        with self._session_scope() as session:
            institution = session.get(Institution, institution_id)
            if not institution:
                return False
            session.delete(institution)
            return True

    # --- Cartões de crédito ---
    def list_credit_cards(self, *, include_inactive: bool = False, institution_id: Optional[int] = None) -> List[dict]:
        session = self.session_factory()
        try:
            query = session.query(CreditCard)
            if institution_id is not None:
                query = query.filter(CreditCard.institution_id == institution_id)
            if not include_inactive:
                query = query.filter(CreditCard.is_active.is_(True))
            cards = query.order_by(CreditCard.name.asc()).all()
            return [card.to_dict() for card in cards]
        finally:
            session.close()

    def create_credit_card(
        self,
        *,
        name: str,
        institution_id: int,
        user_id: int = 1,
        brand: Optional[str] = None,
        last_four_digits: Optional[str] = None,
        closing_day: Optional[int] = None,
        due_day: Optional[int] = None,
        limit_amount: Optional[float] = None,
    ) -> dict:
        clean_name = self._normalize_name(name)
        with self._session_scope() as session:
            institution = session.get(Institution, institution_id)
            if not institution:
                raise ValueError("Instituição financeira não encontrada.")

            self._ensure_unique_credit_card(session, user_id, clean_name)

            card = CreditCard(
                user_id=user_id,
                institution_id=institution_id,
                name=clean_name,
                brand=brand,
                last_four_digits=last_four_digits,
                closing_day=closing_day,
                due_day=due_day,
                limit_amount=limit_amount,
            )
            session.add(card)
            session.flush()
            return card.to_dict()

    def update_credit_card(
        self,
        card_id: int,
        *,
        name: Optional[str] = None,
        brand: Optional[str] = None,
        last_four_digits: Optional[str] = None,
        closing_day: Optional[int] = None,
        due_day: Optional[int] = None,
        limit_amount: Optional[float] = None,
        is_active: Optional[bool] = None,
        institution_id: Optional[int] = None,
    ) -> Optional[dict]:
        with self._session_scope() as session:
            card = session.get(CreditCard, card_id)
            if not card:
                return None

            new_name = self._normalize_name(name) if name is not None else card.name
            if name is not None:
                self._ensure_unique_credit_card(session, card.user_id, new_name, exclude_id=card.id)

            institution_id_to_use = card.institution_id
            if institution_id is not None:
                institution = session.get(Institution, institution_id)
                if not institution:
                    raise ValueError("Instituição financeira não encontrada.")
                institution_id_to_use = institution_id

            card.apply_updates(
                name=new_name if name is not None else None,
                brand=brand,
                last_four_digits=last_four_digits,
                closing_day=closing_day,
                due_day=due_day,
                limit_amount=limit_amount,
                is_active=is_active,
                institution_id=institution_id_to_use if institution_id is not None else None,
            )
            session.flush()
            return card.to_dict()

    def delete_credit_card(self, card_id: int) -> bool:
        with self._session_scope() as session:
            card = session.get(CreditCard, card_id)
            if not card:
                return False
            session.delete(card)
            return True

    # --- Tipos de investimento ---
    def list_investment_types(self) -> List[dict]:
        session = self.session_factory()
        try:
            items = session.query(InvestmentType).order_by(InvestmentType.name.asc()).all()
            return [it.to_dict() for it in items]
        finally:
            session.close()

    def create_investment_type(
        self,
        *,
        name: str,
        classification: Optional[str] = None,
        description: Optional[str] = None,
    ) -> dict:
        clean_name = self._normalize_name(name)
        with self._session_scope() as session:
            self._ensure_unique_investment_type(session, clean_name)

            item = InvestmentType(
                name=clean_name,
                classification=classification,
                description=description,
            )
            session.add(item)
            session.flush()
            return item.to_dict()

    def update_investment_type(
        self,
        item_id: int,
        *,
        name: Optional[str] = None,
        classification: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Optional[dict]:
        with self._session_scope() as session:
            item = session.get(InvestmentType, item_id)
            if not item:
                return None

            new_name = self._normalize_name(name) if name is not None else item.name
            if name is not None:
                self._ensure_unique_investment_type(session, new_name, exclude_id=item.id)

            item.apply_updates(
                name=new_name if name is not None else None,
                classification=classification,
                description=description,
            )
            session.flush()
            return item.to_dict()

    def delete_investment_type(self, item_id: int) -> bool:
        with self._session_scope() as session:
            item = session.get(InvestmentType, item_id)
            if not item:
                return False
            session.delete(item)
            return True

    # --- Helpers ---
    def _parse_category_type(self, category_type: str) -> Optional[CategoryType]:
        if category_type is None:
            return None

        normalized = category_type.strip().lower()
        aliases = {
            "income": CategoryType.INCOME,
            "receita": CategoryType.INCOME,
            "receitas": CategoryType.INCOME,
            "expense": CategoryType.EXPENSE,
            "despesa": CategoryType.EXPENSE,
            "despesas": CategoryType.EXPENSE,
        }
        return aliases.get(normalized)

    def _normalize_name(self, name: str) -> str:
        if not name or not name.strip():
            raise ValueError("Nome é obrigatório.")
        return name.strip()

    def _ensure_unique_category(
        self,
        session: Session,
        user_id: int,
        name: str,
        parent_id: Optional[int],
        *,
        exclude_id: Optional[int] = None,
    ) -> None:
        query = session.query(Category).filter(
            Category.user_id == user_id,
            func.lower(Category.name) == func.lower(name),
            Category.parent_id.is_(parent_id) if parent_id is None else Category.parent_id == parent_id,
        )
        if exclude_id:
            query = query.filter(Category.id != exclude_id)
        if session.query(query.exists()).scalar():
            raise ValueError("Já existe uma categoria com este nome neste nível.")

    def _ensure_unique_institution(
        self,
        session: Session,
        user_id: int,
        name: str,
        *,
        exclude_id: Optional[int] = None,
    ) -> None:
        query = session.query(Institution).filter(
            Institution.user_id == user_id,
            func.lower(Institution.name) == func.lower(name),
        )
        if exclude_id:
            query = query.filter(Institution.id != exclude_id)
        if session.query(query.exists()).scalar():
            raise ValueError("Já existe uma instituição com este nome.")

    def _ensure_unique_credit_card(
        self,
        session: Session,
        user_id: int,
        name: str,
        *,
        exclude_id: Optional[int] = None,
    ) -> None:
        query = session.query(CreditCard).filter(
            CreditCard.user_id == user_id,
            func.lower(CreditCard.name) == func.lower(name),
        )
        if exclude_id:
            query = query.filter(CreditCard.id != exclude_id)
        if session.query(query.exists()).scalar():
            raise ValueError("Já existe um cartão com este nome.")

    def _ensure_unique_investment_type(
        self,
        session: Session,
        name: str,
        *,
        exclude_id: Optional[int] = None,
    ) -> None:
        query = session.query(InvestmentType).filter(func.lower(InvestmentType.name) == func.lower(name))
        if exclude_id:
            query = query.filter(InvestmentType.id != exclude_id)
        if session.query(query.exists()).scalar():
            raise ValueError("Já existe um tipo de investimento com este nome.")
