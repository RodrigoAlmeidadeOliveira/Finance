"""
Serviço de consolidação financeira (sumários e controles mensais).
"""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, date
from typing import Callable, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from ..models import PendingTransaction, ReviewStatus, Category


def _parse_date(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


class AnalyticsService:
    """
    Calcula sumários por período usando PendingTransaction (após revisão).
    """

    def __init__(self, session_factory: Callable[[], Session]):
        self.session_factory = session_factory

    def summary(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        include_pending: bool = False,
    ) -> Dict:
        start_dt = _parse_date(start_date)
        end_dt = _parse_date(end_date)

        session = self.session_factory()
        try:
            query = session.query(PendingTransaction)
            if start_dt:
                query = query.filter(PendingTransaction.date >= start_dt)
            if end_dt:
                query = query.filter(PendingTransaction.date <= end_dt)

            if not include_pending:
                query = query.filter(
                    PendingTransaction.review_status.in_(
                        [ReviewStatus.APPROVED, ReviewStatus.MODIFIED]
                    )
                )

            txs: List[PendingTransaction] = query.all()
            return self._build_summary(txs)
        finally:
            session.close()

    def monthly_by_category(
        self,
        months_back: int = 6,
        include_pending: bool = False,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        include_planned: bool = True,
    ) -> Dict:
        """
        Retorna uma matriz mensal por categoria, separando receitas e despesas.
        """
        start_dt = _parse_date(start_date)
        end_dt = _parse_date(end_date)

        session = self.session_factory()
        try:
            category_map = {c.name: c for c in session.query(Category).all()}

            planned_map: Dict[str, Dict[str, float]] = defaultdict(dict)
            if include_planned:
                from ..models import CategoryRecurringPlan  # avoid circular
                recurring = session.query(CategoryRecurringPlan).all()
                for r in recurring:
                    cat = None
                    # reverse lookup by name? we have only id; need name
                # Build map category_id->name
                cat_id_to_name = {c.id: c.name for c in category_map.values() if hasattr(c, "id")}
                for r in session.query(CategoryRecurringPlan).all():
                    cat_name = cat_id_to_name.get(r.category_id, None)
                    if not cat_name:
                        continue
                    current = r.start_date
                    end = r.end_date
                    while True:
                        key_month = f"{current.year:04d}-{current.month:02d}"
                        planned_map[cat_name][key_month] = planned_map[cat_name].get(key_month, 0.0) + r.amount
                        # advance one month
                        if end and (current.year > end.year or (current.year == end.year and current.month >= end.month)):
                            break
                        if end is None and current > datetime.utcnow().date():
                            break
                        next_month = current.month + 1
                        next_year = current.year + 1 if next_month > 12 else current.year
                        next_month = 1 if next_month > 12 else next_month
                        current = current.replace(year=next_year, month=next_month, day=1)
                        if end and current > end:
                            break

            query = session.query(PendingTransaction)
            if start_dt:
                query = query.filter(PendingTransaction.date >= start_dt)
            if end_dt:
                query = query.filter(PendingTransaction.date <= end_dt)
            if not include_pending:
                query = query.filter(
                    PendingTransaction.review_status.in_(
                        [ReviewStatus.APPROVED, ReviewStatus.MODIFIED]
                    )
                )

            txs: List[PendingTransaction] = query.all()

            buckets: Dict[str, Dict] = {}
            months_set = set()
            for tx in txs:
                dt: date = tx.date.date()
                key_month = f"{dt.year:04d}-{dt.month:02d}"
                months_set.add((dt.year, dt.month, key_month))
                name = tx.final_category or tx.user_category or tx.predicted_category or "Sem categoria"
                if name not in buckets:
                    buckets[name] = {"values": {}, "pos": 0.0, "neg": 0.0}
                value = tx.amount
                if value >= 0:
                    buckets[name]["pos"] += value
                else:
                    buckets[name]["neg"] += value
                buckets[name]["values"][key_month] = buckets[name]["values"].get(key_month, 0.0) + value

            ordered_months = sorted(months_set, key=lambda x: (x[0], x[1]), reverse=True)
            if not start_dt or not end_dt:
                ordered_months = ordered_months[:months_back]
            ordered_months.sort(key=lambda x: (x[0], x[1]))

            months_meta = [{"year": y, "month": m, "key": key} for y, m, key in ordered_months]
            categories = []
            for name, values in buckets.items():
                cat_type = None
                if name in category_map and getattr(category_map[name], "type", None):
                    cat_type = category_map[name].type.value
                else:
                    # infer: se despesas (negativo dominante) marcar expense, senão income
                    cat_type = "expense" if abs(values["neg"]) >= values["pos"] else "income"

                planned_values = {}
                if include_planned and name in planned_map:
                    for m in months_meta:
                        planned_raw = planned_map[name].get(m["key"], 0.0)
                        if planned_raw:
                            planned_values[m["key"]] = -planned_raw if cat_type == "expense" else planned_raw

                entry = {
                    "name": name,
                    "category_type": cat_type,
                    "values": {
                        m["key"]: {
                            "actual": round(values["values"].get(m["key"], 0.0), 2),
                            "planned": round(planned_values.get(m["key"], 0.0), 2) if include_planned else 0.0,
                        }
                        for m in months_meta
                    },
                }
                categories.append(entry)

            categories.sort(key=lambda c: c["name"].lower())
            return {"months": months_meta, "categories": categories}
        finally:
            session.close()

    def monthly(
        self,
        months_back: int = 6,
        include_pending: bool = False,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict:
        """
        Retorna série mensal de receitas, despesas e saldo para os últimos N meses.
        """
        start_dt = _parse_date(start_date)
        end_dt = _parse_date(end_date)

        session = self.session_factory()
        try:
            query = session.query(PendingTransaction)
            if start_dt:
                query = query.filter(PendingTransaction.date >= start_dt)
            if end_dt:
                query = query.filter(PendingTransaction.date <= end_dt)

            if not include_pending:
                query = query.filter(
                    PendingTransaction.review_status.in_(
                        [ReviewStatus.APPROVED, ReviewStatus.MODIFIED]
                    )
                )

            txs: List[PendingTransaction] = query.all()
            buckets: Dict[Tuple[int, int], Dict[str, float]] = defaultdict(
                lambda: {"income": 0.0, "expense": 0.0}
            )

            for tx in txs:
                dt: date = tx.date.date()
                key = (dt.year, dt.month)
                if tx.amount >= 0:
                    buckets[key]["income"] += tx.amount
                else:
                    buckets[key]["expense"] += abs(tx.amount)

            # ordenar por ano/mes e limitar últimos months_back
            ordered_keys = sorted(buckets.keys(), reverse=True)
            if not start_dt or not end_dt:
                ordered_keys = ordered_keys[:months_back]
            ordered_keys.reverse()

            series = []
            for year, month in ordered_keys:
                income = buckets[(year, month)]["income"]
                expense = buckets[(year, month)]["expense"]
                series.append(
                    {
                        "year": year,
                        "month": month,
                        "income": income,
                        "expense": expense,
                        "balance": income - expense,
                    }
                )

            return {"series": series}
        finally:
            session.close()

    def compare_periods(
        self,
        *,
        start: Optional[str],
        end: Optional[str],
        compare_start: Optional[str] = None,
        compare_end: Optional[str] = None,
        include_pending: bool = False,
    ) -> Dict:
        """
        Compara dois períodos e retorna deltas de totais e status.
        Quando compare_* não for informado, usa período anterior de mesmo tamanho.
        """
        start_dt = _parse_date(start)
        end_dt = _parse_date(end)

        if start_dt and end_dt and not compare_start and not compare_end:
            span = end_dt - start_dt
            compare_end_dt = start_dt
            compare_start_dt = compare_end_dt - span
        else:
            compare_start_dt = _parse_date(compare_start)
            compare_end_dt = _parse_date(compare_end)

        session = self.session_factory()
        try:
            def _fetch_summary(s_dt, e_dt):
                query = session.query(PendingTransaction)
                if s_dt:
                    query = query.filter(PendingTransaction.date >= s_dt)
                if e_dt:
                    query = query.filter(PendingTransaction.date <= e_dt)
                if not include_pending:
                    query = query.filter(
                        PendingTransaction.review_status.in_(
                            [ReviewStatus.APPROVED, ReviewStatus.MODIFIED]
                        )
                    )
                return self._build_summary(query.all())

            current = _fetch_summary(start_dt, end_dt)
            previous = _fetch_summary(compare_start_dt, compare_end_dt)

            def _delta(field):
                return round((current["totals"].get(field, 0) - previous["totals"].get(field, 0)), 2)

            return {
                "current": current,
                "previous": previous,
                "deltas": {
                    "income": _delta("income"),
                    "expense": _delta("expense"),
                    "balance": _delta("balance"),
                },
            }
        finally:
            session.close()

    # --- helpers ---
    def _build_summary(self, txs: List[PendingTransaction]) -> Dict:
        totals = {"income": 0.0, "expense": 0.0}
        by_category: Dict[str, Dict[str, float]] = defaultdict(
            lambda: {"income": 0.0, "expense": 0.0}
        )
        by_status: Dict[str, int] = defaultdict(int)

        for tx in txs:
            by_status[tx.review_status.value] += 1
            category = tx.final_category or "Sem categoria"
            if tx.amount >= 0:
                totals["income"] += tx.amount
                by_category[category]["income"] += tx.amount
            else:
                totals["expense"] += abs(tx.amount)
                by_category[category]["expense"] += abs(tx.amount)

        balance = totals["income"] - totals["expense"]

        # ordenar categorias por valor (desc)
        category_list = [
            {
                "name": name,
                "income": data["income"],
                "expense": data["expense"],
                "total": data["income"] - data["expense"],
            }
            for name, data in by_category.items()
        ]
        category_list.sort(key=lambda x: x["total"], reverse=True)

        return {
            "totals": {**totals, "balance": balance},
            "categories": category_list,
            "status_counts": by_status,
            "count": len(txs),
        }
