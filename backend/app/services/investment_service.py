"""
Serviço para CRUD de investimentos e proventos, além de visão de portfólio.
"""
from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime
from typing import Callable, Dict, List, Optional

from sqlalchemy.orm import Session

from ..models import Dividend, Institution, Investment, InvestmentType


def _parse_date(value: Optional[str]):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value).date()
    except ValueError:
        return None


class InvestmentService:
    """Operações de carteira de investimentos."""

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

    # --- Investimentos ---
    def list_investments(self, include_inactive: bool = False) -> List[dict]:
        session = self.session_factory()
        try:
            query = session.query(Investment)
            if not include_inactive:
                query = query.filter(Investment.is_active.is_(True))
            items = query.order_by(Investment.created_at.desc()).all()
            return [item.to_dict() for item in items]
        finally:
            session.close()

    def get_investment(self, investment_id: int) -> Optional[dict]:
        session = self.session_factory()
        try:
            item = session.get(Investment, investment_id)
            if not item:
                return None
            data = item.to_dict()
            data["dividends"] = [d.to_dict() for d in item.dividends]
            return data
        finally:
            session.close()

    def create_investment(
        self,
        *,
        name: str,
        amount_invested: float,
        current_value: Optional[float] = None,
        institution_id: Optional[int] = None,
        investment_type_id: Optional[int] = None,
        classification: Optional[str] = None,
        applied_at: Optional[str] = None,
        maturity_date: Optional[str] = None,
        profitability_rate: Optional[float] = None,
        notes: Optional[str] = None,
        user_id: int = 1,
    ) -> dict:
        if amount_invested < 0:
            raise ValueError("amount_invested não pode ser negativo.")

        applied_dt = _parse_date(applied_at)
        maturity_dt = _parse_date(maturity_date)

        with self._session_scope() as session:
            if institution_id:
                inst = session.get(Institution, institution_id)
                if not inst:
                    raise ValueError("Instituição não encontrada.")
            if investment_type_id:
                inv_type = session.get(InvestmentType, investment_type_id)
                if not inv_type:
                    raise ValueError("Tipo de investimento não encontrado.")

            item = Investment(
                user_id=user_id,
                name=name.strip(),
                institution_id=institution_id,
                investment_type_id=investment_type_id,
                classification=classification,
                amount_invested=amount_invested,
                current_value=current_value if current_value is not None else amount_invested,
                applied_at=applied_dt,
                maturity_date=maturity_dt,
                profitability_rate=profitability_rate,
                notes=notes,
            )
            session.add(item)
            session.flush()
            return item.to_dict()

    def update_investment(
        self,
        investment_id: int,
        *,
        name: Optional[str] = None,
        amount_invested: Optional[float] = None,
        current_value: Optional[float] = None,
        institution_id: Optional[int] = None,
        investment_type_id: Optional[int] = None,
        classification: Optional[str] = None,
        applied_at: Optional[str] = None,
        maturity_date: Optional[str] = None,
        profitability_rate: Optional[float] = None,
        notes: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> Optional[dict]:
        with self._session_scope() as session:
            item = session.get(Investment, investment_id)
            if not item:
                return None

            applied_dt = _parse_date(applied_at) if applied_at is not None else None
            maturity_dt = _parse_date(maturity_date) if maturity_date is not None else None

            if institution_id:
                inst = session.get(Institution, institution_id)
                if not inst:
                    raise ValueError("Instituição não encontrada.")
            if investment_type_id:
                inv_type = session.get(InvestmentType, investment_type_id)
                if not inv_type:
                    raise ValueError("Tipo de investimento não encontrado.")

            item.apply_updates(
                name=name,
                institution_id=institution_id,
                investment_type_id=investment_type_id,
                classification=classification,
                amount_invested=amount_invested,
                current_value=current_value,
                applied_at=applied_dt if applied_at is not None else None,
                maturity_date=maturity_dt if maturity_date is not None else None,
                profitability_rate=profitability_rate,
                notes=notes,
                is_active=is_active,
            )
            session.flush()
            return item.to_dict()

    def delete_investment(self, investment_id: int) -> bool:
        with self._session_scope() as session:
            item = session.get(Investment, investment_id)
            if not item:
                return False
            session.delete(item)
            return True

    # --- Dividends / proventos ---
    def add_dividend(
        self,
        *,
        investment_id: int,
        amount: float,
        description: Optional[str] = None,
        received_at: Optional[str] = None,
        user_id: int = 1,
    ) -> dict:
        if amount <= 0:
            raise ValueError("amount deve ser maior que zero.")
        received_dt = _parse_date(received_at)

        with self._session_scope() as session:
            inv = session.get(Investment, investment_id)
            if not inv:
                raise ValueError("Investimento não encontrado.")

            dividend = Dividend(
                investment_id=investment_id,
                user_id=user_id,
                amount=amount,
                description=description,
                received_at=received_dt,
            )
            session.add(dividend)

            # opcional: soma no valor atual
            inv.current_value = (inv.current_value or 0) + amount
            session.flush()
            return dividend.to_dict()

    def delete_dividend(self, dividend_id: int) -> bool:
        with self._session_scope() as session:
            item = session.get(Dividend, dividend_id)
            if not item:
                return False
            session.delete(item)
            return True

    # --- Portfolio summary ---
    def portfolio_summary(self) -> Dict:
        session = self.session_factory()
        try:
            items = session.query(Investment).all()
            total_invested = sum(inv.amount_invested or 0 for inv in items)
            total_current = sum(inv.current_value or 0 for inv in items)
            total_gain = total_current - total_invested
            by_class = {}
            for inv in items:
                key = (inv.classification or "indefinido").lower()
                by_class.setdefault(key, {"invested": 0, "current": 0})
                by_class[key]["invested"] += inv.amount_invested or 0
                by_class[key]["current"] += inv.current_value or 0

            return {
                "total_invested": round(total_invested, 2),
                "total_current": round(total_current, 2),
                "total_gain": round(total_gain, 2),
                "by_classification": {
                    k: {
                        "invested": round(v["invested"], 2),
                        "current": round(v["current"], 2),
                        "gain": round(v["current"] - v["invested"], 2),
                    }
                    for k, v in by_class.items()
                },
                "count": len(items),
            }
        finally:
            session.close()

    def redeem(
        self,
        *,
        investment_id: int,
        amount: Optional[float] = None,
        close_position: bool = False,
    ) -> Optional[dict]:
        """
        Registra resgate parcial/total. Se close_position=True marca is_active=False.
        amount: valor resgatado; se None usa current_value (encerra total).
        """
        with self._session_scope() as session:
            inv = session.get(Investment, investment_id)
            if not inv:
                return None

            value = amount if amount is not None else (inv.current_value or 0)
            if value < 0:
                raise ValueError("amount não pode ser negativo.")
            if value > (inv.current_value or 0):
                raise ValueError("amount maior que o valor atual.")

            inv.current_value = (inv.current_value or 0) - value
            if close_position:
                inv.is_active = False

            session.flush()
            return inv.to_dict()

    def performance(self) -> List[dict]:
        """
        Lista cada investimento com ganho absoluto e percentual.
        """
        session = self.session_factory()
        try:
            items = session.query(Investment).all()
            result = []
            for inv in items:
                invested = inv.amount_invested or 0
                current = inv.current_value or 0
                gain = current - invested
                roi = (gain / invested * 100) if invested else 0
                data = inv.to_dict()
                data.update(
                    {
                        "gain": round(gain, 2),
                        "roi": round(roi, 2),
                    }
                )
                result.append(data)
            return result
        finally:
            session.close()
