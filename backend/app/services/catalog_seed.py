"""
Utilitário para popular cadastros base a partir dos dados já importados.
"""
from __future__ import annotations

from contextlib import contextmanager
from typing import Callable, Dict, List, Optional, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session

from ..models import Category, CategoryType, ImportBatch, Institution, PendingTransaction


class CatalogSeeder:
    """
    Cria registros iniciais de categorias e instituições com base nas importações já existentes.
    """

    DEFAULT_ACCOUNT_TYPE = "corrente"

    def __init__(self, session_factory: Callable[[], Session]):
        self.session_factory = session_factory

    @contextmanager
    def _session_scope(self) -> Session:
        session = self.session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def seed_from_imports(self) -> Dict[str, int]:
        """
        Popula categorias e instituições a partir de pending_transactions e import_batches.
        """
        with self._session_scope() as session:
            institutions_created = self._seed_institutions(session)
            categories_created = self._seed_categories(session)

            return {
                "institutions_created": institutions_created,
                "categories_created": categories_created,
            }

    # --- Internals ---
    def _seed_institutions(self, session: Session) -> int:
        existing = {
            inst.name.lower(): inst
            for inst in session.query(Institution).all()
        }
        created = 0

        batches: List[Tuple[Optional[str], Optional[float]]] = (
            session.query(ImportBatch.institution_name, ImportBatch.balance)
            .filter(ImportBatch.institution_name.isnot(None))
            .all()
        )
        for name, balance in batches:
            if not name:
                continue
            key = name.strip().lower()
            if key in existing:
                # Atualiza saldo atual se fornecido
                if balance is not None and existing[key].current_balance == 0:
                    existing[key].current_balance = balance
                continue

            inst = Institution(
                name=name.strip(),
                account_type=self.DEFAULT_ACCOUNT_TYPE,
                current_balance=balance or 0.0,
                initial_balance=balance or 0.0,
            )
            session.add(inst)
            existing[key] = inst
            created += 1
        return created

    def _seed_categories(self, session: Session) -> int:
        existing = {
            (cat.name.lower(), cat.type): cat
            for cat in session.query(Category).all()
        }
        created = 0

        tx_rows: List[Tuple[Optional[str], float]] = (
            session.query(PendingTransaction.user_category, PendingTransaction.predicted_category, PendingTransaction.amount)
            .all()
        )
        for user_cat, predicted_cat, amount in tx_rows:
            name = (user_cat or predicted_cat or "").strip()
            if not name:
                continue

            cat_type = CategoryType.EXPENSE if amount < 0 else CategoryType.INCOME
            key = (name.lower(), cat_type)
            if key in existing:
                continue

            cat = Category(
                name=name,
                type=cat_type,
            )
            session.add(cat)
            existing[key] = cat
            created += 1

        return created
