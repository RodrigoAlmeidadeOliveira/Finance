"""
Endpoints para planos financeiros e projeções de receita.
"""
from __future__ import annotations

from flask import Blueprint, jsonify, request

from ..database import get_session
from ..services.planning_service import PlanningService

planning_bp = Blueprint("planning", __name__, url_prefix="/api")


def _bool_arg(name: str, default: bool = False) -> bool:
    value = request.args.get(name)
    if value is None:
        return default
    return str(value).lower() in {"1", "true", "yes", "on"}


def _planning_service() -> PlanningService:
    return PlanningService(get_session)

def _int_arg(name: str, default: Optional[int] = None) -> Optional[int]:
    value = request.args.get(name, default=None if default is None else str(default))
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


# --- Plans ---
@planning_bp.get("/plans")
def list_plans():
    service = _planning_service()
    items = service.list_plans(include_inactive=_bool_arg("include_inactive"))
    return jsonify({"items": items})


@planning_bp.post("/plans")
def create_plan():
    data = request.get_json(silent=True) or {}
    try:
        created = _planning_service().create_plan(
            name=data.get("name", ""),
            goal_amount=float(data.get("goal_amount") or 0),
            monthly_contribution=float(data.get("monthly_contribution") or 0),
            current_balance=float(data.get("current_balance") or 0),
            institution_id=data.get("institution_id"),
            partition=data.get("partition"),
            target_date=data.get("target_date"),
            user_id=int(data.get("user_id") or 1),
            notes=data.get("notes"),
        )
    except (ValueError, TypeError) as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify(created), 201


@planning_bp.put("/plans/<int:plan_id>")
def update_plan(plan_id: int):
    data = request.get_json(silent=True) or {}
    try:
        updated = _planning_service().update_plan(
            plan_id,
            name=data.get("name"),
            goal_amount=float(data["goal_amount"]) if "goal_amount" in data else None,
            monthly_contribution=float(data["monthly_contribution"]) if "monthly_contribution" in data else None,
            current_balance=float(data["current_balance"]) if "current_balance" in data else None,
            institution_id=data.get("institution_id"),
            partition=data.get("partition"),
            target_date=data.get("target_date"),
            is_active=data.get("is_active"),
            notes=data.get("notes"),
        )
    except (ValueError, TypeError) as exc:
        return jsonify({"error": str(exc)}), 400
    if not updated:
        return jsonify({"error": "Plano não encontrado"}), 404
    return jsonify(updated)


@planning_bp.delete("/plans/<int:plan_id>")
def delete_plan(plan_id: int):
    deleted = _planning_service().delete_plan(plan_id)
    if not deleted:
        return jsonify({"error": "Plano não encontrado"}), 404
    return ("", 204)


# --- Income projections ---
@planning_bp.get("/income-projections")
def list_income_projections():
    service = _planning_service()
    items = service.list_income_projections(
        include_received=_bool_arg("include_received", True),
        start_date=request.args.get("start"),
        end_date=request.args.get("end"),
    )
    return jsonify({"items": items})


@planning_bp.post("/income-projections")
def create_income_projection():
    data = request.get_json(silent=True) or {}
    try:
        created = _planning_service().create_income_projection(
            description=data.get("description", ""),
            amount=float(data.get("amount") or 0),
            expected_date=data.get("expected_date"),
            projection_type=data.get("projection_type", "fixed"),
            user_id=int(data.get("user_id") or 1),
            received=bool(data.get("received", False)),
        )
    except (ValueError, TypeError) as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify(created), 201


@planning_bp.put("/income-projections/<int:item_id>")
def update_income_projection(item_id: int):
    data = request.get_json(silent=True) or {}
    try:
        updated = _planning_service().update_income_projection(
            item_id,
            description=data.get("description"),
            amount=float(data["amount"]) if "amount" in data else None,
            expected_date=data.get("expected_date"),
            projection_type=data.get("projection_type"),
            received=data.get("received"),
        )
    except (ValueError, TypeError) as exc:
        return jsonify({"error": str(exc)}), 400
    if not updated:
        return jsonify({"error": "Projeção não encontrada"}), 404
    return jsonify(updated)


@planning_bp.delete("/income-projections/<int:item_id>")
def delete_income_projection(item_id: int):
    deleted = _planning_service().delete_income_projection(item_id)
    if not deleted:
        return jsonify({"error": "Projeção não encontrada"}), 404
    return ("", 204)


# --- Planned surplus ---
@planning_bp.get("/plans/surplus")
def planned_surplus():
    data = _planning_service().planned_surplus()
    return jsonify(data)


# --- Planning notes ---
@planning_bp.get("/plans/notes")
def list_notes():
    items = _planning_service().list_notes()
    return jsonify({"items": items})


@planning_bp.post("/plans/notes")
def create_note():
    data = request.get_json(silent=True) or {}
    try:
        note = _planning_service().create_note(content=data.get("content", ""), user_id=int(data.get("user_id") or 1))
    except (ValueError, TypeError) as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify(note), 201


@planning_bp.delete("/plans/notes/<int:note_id>")
def delete_note(note_id: int):
    deleted = _planning_service().delete_note(note_id)
    if not deleted:
        return jsonify({"error": "Nota não encontrada"}), 404
    return ("", 204)


# --- Recorrências por categoria ---
@planning_bp.get("/plans/recurring")
def list_recurring_plans():
    items = _planning_service().list_recurring_plans()
    return jsonify({"items": items})


@planning_bp.post("/plans/recurring")
def create_recurring_plan():
    data = request.get_json(silent=True) or {}
    try:
        item = _planning_service().create_recurring_plan(
            category_id=int(data.get("category_id") or 0),
            amount=float(data.get("amount") or 0),
            start_date=data.get("start_date"),
            end_date=data.get("end_date"),
            user_id=int(data.get("user_id") or 1),
        )
    except (ValueError, TypeError) as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify(item), 201


@planning_bp.delete("/plans/recurring/<int:item_id>")
def delete_recurring_plan(item_id: int):
    deleted = _planning_service().delete_recurring_plan(item_id)
    if not deleted:
        return jsonify({"error": "Recorrência não encontrada"}), 404
    return ("", 204)


# --- Category budgets (planejamento mensal) ---
@planning_bp.get("/plans/budgets")
def list_budgets():
    service = _planning_service()
    items = service.list_category_budgets(
        month=_int_arg("month"),
        year=_int_arg("year"),
    )
    return jsonify({"items": items})


@planning_bp.post("/plans/budgets")
def create_budget():
    data = request.get_json(silent=True) or {}
    try:
        created = _planning_service().upsert_category_budget(
            category_id=int(data.get("category_id") or 0),
            month=int(data.get("month") or 0),
            year=int(data.get("year") or 0),
            amount=float(data.get("amount") or 0),
            user_id=int(data.get("user_id") or 1),
        )
    except (ValueError, TypeError) as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify(created), 201


@planning_bp.put("/plans/budgets/<int:budget_id>")
def update_budget(budget_id: int):
    data = request.get_json(silent=True) or {}
    try:
        updated = _planning_service().upsert_category_budget(
            category_id=int(data.get("category_id") or 0),
            month=int(data.get("month") or 0),
            year=int(data.get("year") or 0),
            amount=float(data.get("amount") or 0),
            user_id=int(data.get("user_id") or 1),
        )
    except (ValueError, TypeError) as exc:
        return jsonify({"error": str(exc)}), 400
    if not updated:
        return jsonify({"error": "Meta não encontrada"}), 404
    return jsonify(updated)


@planning_bp.delete("/plans/budgets/<int:budget_id>")
def delete_budget(budget_id: int):
    deleted = _planning_service().delete_category_budget(budget_id)
    if not deleted:
        return jsonify({"error": "Meta não encontrada"}), 404
    return ("", 204)


@planning_bp.get("/plans/budget-compliance")
def budget_compliance():
    service = _planning_service()
    items = service.budget_compliance(
        start_date=request.args.get("start"),
        end_date=request.args.get("end"),
        include_pending=_bool_arg("include_pending", False),
    )
    return jsonify({"items": items})
