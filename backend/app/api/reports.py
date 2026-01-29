"""
Endpoints de controle mensal e relatórios.
"""
from __future__ import annotations

from flask import Blueprint, jsonify, request

from ..database import get_session
from ..services.analytics_service import AnalyticsService

reports_bp = Blueprint("reports", __name__, url_prefix="/api/reports")


def get_service() -> AnalyticsService:
    return AnalyticsService(get_session)


def _bool_arg(name: str, default: bool = False) -> bool:
    value = request.args.get(name)
    if value is None:
        return default
    return str(value).lower() in {"1", "true", "yes", "on"}


@reports_bp.get("/summary")
def summary():
    service = get_service()
    data = service.summary(
        start_date=request.args.get("start"),
        end_date=request.args.get("end"),
        include_pending=_bool_arg("include_pending"),
    )
    return jsonify(data)


@reports_bp.get("/monthly")
def monthly():
    service = get_service()
    months_back = request.args.get("months", default=6, type=int)
    data = service.monthly(
        months_back=months_back,
        include_pending=_bool_arg("include_pending"),
        start_date=request.args.get("start"),
        end_date=request.args.get("end"),
    )
    return jsonify(data)

@reports_bp.get("/monthly-categories")
def monthly_categories():
    service = get_service()
    months_back = request.args.get("months", default=6, type=int)
    data = service.monthly_by_category(
        months_back=months_back,
        include_pending=_bool_arg("include_pending"),
        start_date=request.args.get("start"),
        end_date=request.args.get("end"),
    )
    return jsonify(data)


@reports_bp.get("/compare")
def compare():
    service = get_service()
    data = service.compare_periods(
        start=request.args.get("start"),
        end=request.args.get("end"),
        compare_start=request.args.get("compare_start"),
        compare_end=request.args.get("compare_end"),
        include_pending=_bool_arg("include_pending"),
    )
    return jsonify(data)
