"""
Serviços de planos financeiros e projeções de receita.
"""
from __future__ import annotations

from contextlib import contextmanager
from datetime import date, datetime
from typing import Callable, List, Optional

from sqlalchemy.orm import Session

from ..models import (
    Category,
    CategoryBudget,
    CategoryType,
    CategoryRecurringPlan,
    FinancialPlan,
    IncomeProjection,
    IncomeProjectionType,
    Institution,
    PendingTransaction,
    PlanningNote,
    ReviewStatus,
)


def _parse_date(value: Optional[str]) -> Optional[date]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value).date()
    except ValueError:
        return None


class PlanningService:
    """CRUD e cálculos simples para planejamento financeiro."""

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

    # --- Financial Plans ---
    def list_plans(self, *, include_inactive: bool = False) -> List[dict]:
        session = self.session_factory()
        try:
            query = session.query(FinancialPlan)
            if not include_inactive:
                query = query.filter(FinancialPlan.is_active.is_(True))
            items = query.order_by(FinancialPlan.created_at.desc()).all()
            return [self._with_progress(p) for p in items]
        finally:
            session.close()

    def create_plan(
        self,
        *,
        name: str,
        goal_amount: float,
        monthly_contribution: float = 0.0,
        current_balance: float = 0.0,
        institution_id: Optional[int] = None,
        partition: Optional[str] = None,
        target_date: Optional[str] = None,
        user_id: int = 1,
        notes: Optional[str] = None,
    ) -> dict:
        if goal_amount <= 0:
            raise ValueError("goal_amount deve ser maior que zero.")

        target_dt = _parse_date(target_date)
        with self._session_scope() as session:
            if institution_id:
                inst = session.get(Institution, institution_id)
                if not inst:
                    raise ValueError("Instituição não encontrada.")

            plan = FinancialPlan(
                user_id=user_id,
                name=name.strip(),
                goal_amount=goal_amount,
                monthly_contribution=monthly_contribution,
                current_balance=current_balance,
                institution_id=institution_id,
                partition=partition,
                target_date=target_dt,
                notes=notes,
            )
            session.add(plan)
            session.flush()
            return self._with_progress(plan)

    def update_plan(
        self,
        plan_id: int,
        *,
        name: Optional[str] = None,
        goal_amount: Optional[float] = None,
        monthly_contribution: Optional[float] = None,
        current_balance: Optional[float] = None,
        institution_id: Optional[int] = None,
        partition: Optional[str] = None,
        target_date: Optional[str] = None,
        is_active: Optional[bool] = None,
        notes: Optional[str] = None,
    ) -> Optional[dict]:
        with self._session_scope() as session:
            plan = session.get(FinancialPlan, plan_id)
            if not plan:
                return None

            target_dt = _parse_date(target_date) if target_date is not None else None
            if institution_id:
                inst = session.get(Institution, institution_id)
                if not inst:
                    raise ValueError("Instituição não encontrada.")

            plan.apply_updates(
                name=name,
                goal_amount=goal_amount,
                monthly_contribution=monthly_contribution,
                current_balance=current_balance,
                institution_id=institution_id,
                partition=partition,
                target_date=target_dt if target_date is not None else None,
                is_active=is_active,
                notes=notes,
            )
            session.flush()
            return self._with_progress(plan)

    def delete_plan(self, plan_id: int) -> bool:
        with self._session_scope() as session:
            plan = session.get(FinancialPlan, plan_id)
            if not plan:
                return False
            session.delete(plan)
            return True

    # --- Income projections ---
    def list_income_projections(
        self,
        *,
        include_received: bool = True,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> List[dict]:
        session = self.session_factory()
        try:
            query = session.query(IncomeProjection)

            if start_date:
                start_dt = _parse_date(start_date)
                if start_dt:
                    query = query.filter(IncomeProjection.expected_date >= start_dt)

            if end_date:
                end_dt = _parse_date(end_date)
                if end_dt:
                    query = query.filter(IncomeProjection.expected_date <= end_dt)

            if not include_received:
                query = query.filter(IncomeProjection.received.is_(False))

            items = query.order_by(IncomeProjection.expected_date.asc()).all()
            return [item.to_dict() for item in items]
        finally:
            session.close()

    def create_income_projection(
        self,
        *,
        description: str,
        amount: float,
        expected_date: str,
        projection_type: str = "fixed",
        user_id: int = 1,
        received: bool = False,
    ) -> dict:
        if amount <= 0:
            raise ValueError("amount deve ser maior que zero.")

        parsed_date = _parse_date(expected_date)
        if not parsed_date:
            raise ValueError("expected_date inválida.")

        projection_enum = self._parse_projection_type(projection_type)
        if not projection_enum:
            raise ValueError("projection_type inválido. Use 'fixed' ou 'extra'.")

        with self._session_scope() as session:
            item = IncomeProjection(
                user_id=user_id,
                description=description.strip(),
                amount=amount,
                expected_date=parsed_date,
                projection_type=projection_enum,
                received=received,
            )
            session.add(item)
            session.flush()
            return item.to_dict()

    def update_income_projection(
        self,
        item_id: int,
        *,
        description: Optional[str] = None,
        amount: Optional[float] = None,
        expected_date: Optional[str] = None,
        projection_type: Optional[str] = None,
        received: Optional[bool] = None,
    ) -> Optional[dict]:
        with self._session_scope() as session:
            item = session.get(IncomeProjection, item_id)
            if not item:
                return None

            projection_enum = None
            if projection_type is not None:
                projection_enum = self._parse_projection_type(projection_type)
                if not projection_enum:
                    raise ValueError("projection_type inválido. Use 'fixed' ou 'extra'.")

            parsed_date = _parse_date(expected_date) if expected_date is not None else None

            item.apply_updates(
                description=description,
                amount=amount,
                expected_date=parsed_date if expected_date is not None else None,
                projection_type=projection_enum,
                received=received,
            )
            session.flush()
            return item.to_dict()

    def delete_income_projection(self, item_id: int) -> bool:
        with self._session_scope() as session:
            item = session.get(IncomeProjection, item_id)
            if not item:
                return False
            session.delete(item)
            return True

    # --- Planning notes ---
    def list_notes(self) -> List[dict]:
        session = self.session_factory()
        try:
            items = session.query(PlanningNote).order_by(PlanningNote.created_at.desc()).all()
            return [i.to_dict() for i in items]
        finally:
            session.close()

    def create_note(self, content: str, *, user_id: int = 1) -> dict:
        if not content or not content.strip():
            raise ValueError("Conteúdo da nota é obrigatório.")
        with self._session_scope() as session:
            note = PlanningNote(user_id=user_id, content=content.strip())
            session.add(note)
            session.flush()
            return note.to_dict()

    def delete_note(self, note_id: int) -> bool:
        with self._session_scope() as session:
            note = session.get(PlanningNote, note_id)
            if not note:
                return False
            session.delete(note)
            return True

    # --- Planned surplus (receitas projetadas - orçamentos de despesa) ---
    def planned_surplus(self) -> dict:
        session = self.session_factory()
        try:
            projections = session.query(IncomeProjection).filter(IncomeProjection.received.is_(False)).all()
            projected_income = sum(p.amount or 0 for p in projections)

            budgets = session.query(CategoryBudget).all()
            categories = {c.id: c for c in session.query(Category).all()}
            expense_budget = 0.0
            for b in budgets:
                cat = categories.get(b.category_id)
                if cat and cat.type == CategoryType.EXPENSE:
                    expense_budget += b.amount or 0

            surplus = projected_income - expense_budget
            return {
                "projected_income": round(projected_income, 2),
                "expense_budget": round(expense_budget, 2),
                "planned_surplus": round(surplus, 2),
            }
        finally:
            session.close()

    # --- Recorrências por categoria ---
    def list_recurring_plans(self) -> List[dict]:
        session = self.session_factory()
        try:
            items = session.query(CategoryRecurringPlan).order_by(CategoryRecurringPlan.start_date.asc()).all()
            return [i.to_dict() for i in items]
        finally:
            session.close()

    def create_recurring_plan(
        self,
        *,
        category_id: int,
        amount: float,
        start_date: str,
        end_date: Optional[str] = None,
        user_id: int = 1,
    ) -> dict:
        if amount <= 0:
            raise ValueError("amount deve ser maior que zero.")
        start_dt = _parse_date(start_date)
        end_dt = _parse_date(end_date) if end_date else None
        if not start_dt:
            raise ValueError("start_date inválida.")

        with self._session_scope() as session:
            cat = session.get(Category, category_id)
            if not cat:
                raise ValueError("Categoria não encontrada.")

            item = CategoryRecurringPlan(
                user_id=user_id,
                category_id=category_id,
                amount=amount,
                start_date=start_dt,
                end_date=end_dt,
            )
            session.add(item)
            session.flush()
            return item.to_dict()

    def delete_recurring_plan(self, plan_id: int) -> bool:
        with self._session_scope() as session:
            item = session.get(CategoryRecurringPlan, plan_id)
            if not item:
                return False
            session.delete(item)
            return True

    # --- helpers ---
    def _parse_projection_type(self, value: Optional[str]) -> Optional[IncomeProjectionType]:
        if value is None:
            return None
        normalized = value.strip().lower()
        mapping = {
            "fixed": IncomeProjectionType.FIXED,
            "extra": IncomeProjectionType.EXTRA,
        }
        return mapping.get(normalized)

    def _with_progress(self, plan: FinancialPlan) -> dict:
        data = plan.to_dict()
        progress = (plan.current_balance / plan.goal_amount) * 100 if plan.goal_amount else 0
        data["progress"] = round(progress, 2)
        return data

    # --- Budgets per category (planning mensal) ---
    def list_category_budgets(self, *, month: Optional[int] = None, year: Optional[int] = None) -> List[dict]:
        session = self.session_factory()
        try:
            query = session.query(CategoryBudget)
            if month:
                query = query.filter(CategoryBudget.month == int(month))
            if year:
                query = query.filter(CategoryBudget.year == int(year))
            items = query.order_by(CategoryBudget.year.desc(), CategoryBudget.month.desc()).all()

            # enriquecido com nome/tipo da categoria
            categories = {c.id: c for c in session.query(Category).all()}
            result = []
            for item in items:
                cat = categories.get(item.category_id)
                payload = item.to_dict()
                payload["category_name"] = cat.name if cat else None
                payload["category_type"] = cat.type.value if cat and cat.type else None
                result.append(payload)
            return result
        finally:
            session.close()

    def upsert_category_budget(
        self,
        *,
        category_id: int,
        month: int,
        year: int,
        amount: float,
        user_id: int = 1,
    ) -> dict:
        if amount <= 0:
            raise ValueError("amount deve ser maior que zero.")
        if not (1 <= month <= 12):
            raise ValueError("month deve estar entre 1 e 12.")

        with self._session_scope() as session:
            category = session.get(Category, category_id)
            if not category:
                raise ValueError("Categoria não encontrada.")

            existing = (
                session.query(CategoryBudget)
                .filter(
                    CategoryBudget.category_id == category_id,
                    CategoryBudget.month == month,
                    CategoryBudget.year == year,
                    CategoryBudget.user_id == user_id,
                )
                .first()
            )
            if existing:
                existing.amount = amount
                session.flush()
                return existing.to_dict()

            item = CategoryBudget(
                user_id=user_id,
                category_id=category_id,
                month=month,
                year=year,
                amount=amount,
            )
            session.add(item)
            session.flush()
            return item.to_dict()

    def delete_category_budget(self, budget_id: int) -> bool:
        with self._session_scope() as session:
            item = session.get(CategoryBudget, budget_id)
            if not item:
                return False
            session.delete(item)
            return True

    def budget_compliance(
        self,
        *,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        include_pending: bool = False,
    ) -> List[dict]:
        """
        Retorna lista de metas vs realizado por categoria no período informado.
        """
        start_dt = _parse_date(start_date)
        end_dt = _parse_date(end_date)

        session = self.session_factory()
        try:
            budgets = session.query(CategoryBudget).all()
            categories = {c.id: c for c in session.query(Category).all()}

            # busca transações filtradas
            tx_query = session.query(PendingTransaction)
            if start_dt:
                tx_query = tx_query.filter(PendingTransaction.date >= start_dt)
            if end_dt:
                tx_query = tx_query.filter(PendingTransaction.date <= end_dt)
            if not include_pending:
                tx_query = tx_query.filter(
                    PendingTransaction.review_status.in_(
                        [ReviewStatus.APPROVED, ReviewStatus.MODIFIED]
                    )
                )
            txs = tx_query.all()

            # agrega por nome de categoria para compararmos com meta
            tx_by_name = {}
            for tx in txs:
                name = (tx.final_category or tx.user_category or tx.predicted_category or "").strip()
                if not name:
                    continue
                if name not in tx_by_name:
                    tx_by_name[name] = 0.0
                tx_by_name[name] += tx.amount

            results = []
            for b in budgets:
                cat = categories.get(b.category_id)
                cat_name = cat.name if cat else ""
                actual_raw = tx_by_name.get(cat_name, 0.0)

                # normaliza sinal: meta sempre positiva; realizado vira positivo (abs) para despesas
                if cat and cat.type == CategoryType.EXPENSE:
                    actual = abs(actual_raw if actual_raw is not None else 0.0)
                else:
                    actual = actual_raw if actual_raw is not None else 0.0

                target = b.amount
                delta = target - actual

                status = "ok"
                if cat and cat.type == CategoryType.INCOME:
                    # meta de receita: precisa alcançar ou ultrapassar
                    status = "ok" if actual >= target else "alerta"
                else:
                    # meta de despesa: precisa ficar abaixo
                    status = "ok" if actual <= target else "alerta"

                results.append(
                    {
                        "budget_id": b.id,
                        "category_id": b.category_id,
                        "category_name": cat_name,
                        "category_type": cat.type.value if cat and cat.type else None,
                        "month": b.month,
                        "year": b.year,
                        "target": target,
                        "actual": round(actual, 2),
                        "delta": round(delta, 2),
                        "status": status,
                    }
                )

            return results
        finally:
            session.close()
