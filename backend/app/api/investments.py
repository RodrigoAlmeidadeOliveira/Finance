"""
Endpoints para carteira de investimentos e proventos.
"""
from __future__ import annotations

from flask import Blueprint, jsonify, request

from ..database import get_session
from ..services.investment_service import InvestmentService

investments_bp = Blueprint("investments", __name__, url_prefix="/api/investments")


def _service() -> InvestmentService:
    return InvestmentService(get_session)


@investments_bp.get("")
def list_investments():
    items = _service().list_investments(include_inactive=str(request.args.get("include_inactive", "")).lower() in {"1", "true", "yes", "on"})
    return jsonify({"items": items})


@investments_bp.post("")
def create_investment():
    data = request.get_json(silent=True) or {}
    try:
        created = _service().create_investment(
            name=data.get("name", ""),
            amount_invested=float(data.get("amount_invested") or 0),
            current_value=float(data.get("current_value")) if data.get("current_value") is not None else None,
            institution_id=data.get("institution_id"),
            investment_type_id=data.get("investment_type_id"),
            classification=data.get("classification"),
            applied_at=data.get("applied_at"),
            maturity_date=data.get("maturity_date"),
            profitability_rate=float(data.get("profitability_rate")) if data.get("profitability_rate") is not None else None,
            notes=data.get("notes"),
            user_id=int(data.get("user_id") or 1),
        )
    except (ValueError, TypeError) as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify(created), 201


@investments_bp.get("/<int:item_id>")
def get_investment(item_id: int):
    item = _service().get_investment(item_id)
    if not item:
        return jsonify({"error": "Investimento não encontrado"}), 404
    return jsonify(item)


@investments_bp.put("/<int:item_id>")
def update_investment(item_id: int):
    data = request.get_json(silent=True) or {}
    try:
        updated = _service().update_investment(
            item_id,
            name=data.get("name"),
            amount_invested=float(data["amount_invested"]) if "amount_invested" in data else None,
            current_value=float(data["current_value"]) if "current_value" in data else None,
            institution_id=data.get("institution_id"),
            investment_type_id=data.get("investment_type_id"),
            classification=data.get("classification"),
            applied_at=data.get("applied_at"),
            maturity_date=data.get("maturity_date"),
            profitability_rate=float(data["profitability_rate"]) if "profitability_rate" in data else None,
            notes=data.get("notes"),
            is_active=data.get("is_active"),
        )
    except (ValueError, TypeError) as exc:
        return jsonify({"error": str(exc)}), 400
    if not updated:
        return jsonify({"error": "Investimento não encontrado"}), 404
    return jsonify(updated)


@investments_bp.delete("/<int:item_id>")
def delete_investment(item_id: int):
    deleted = _service().delete_investment(item_id)
    if not deleted:
        return jsonify({"error": "Investimento não encontrado"}), 404
    return ("", 204)


# --- dividends ---
@investments_bp.post("/<int:item_id>/dividends")
def add_dividend(item_id: int):
    data = request.get_json(silent=True) or {}
    try:
        created = _service().add_dividend(
            investment_id=item_id,
            amount=float(data.get("amount") or 0),
            description=data.get("description"),
            received_at=data.get("received_at"),
            user_id=int(data.get("user_id") or 1),
        )
    except (ValueError, TypeError) as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify(created), 201


@investments_bp.delete("/dividends/<int:dividend_id>")
def delete_dividend(dividend_id: int):
    deleted = _service().delete_dividend(dividend_id)
    if not deleted:
        return jsonify({"error": "Provento não encontrado"}), 404
    return ("", 204)


@investments_bp.get("/summary")
def portfolio_summary():
    data = _service().portfolio_summary()
    return jsonify(data)


@investments_bp.post("/<int:item_id>/redeem")
def redeem(item_id: int):
    data = request.get_json(silent=True) or {}
    try:
        updated = _service().redeem(
            investment_id=item_id,
            amount=float(data["amount"]) if "amount" in data else None,
            close_position=bool(data.get("close_position", False)),
        )
    except (ValueError, TypeError) as exc:
        return jsonify({"error": str(exc)}), 400
    if not updated:
        return jsonify({"error": "Investimento não encontrado"}), 404
    return jsonify(updated)


@investments_bp.get("/performance")
def performance():
    data = _service().performance()
    return jsonify({"items": data})
