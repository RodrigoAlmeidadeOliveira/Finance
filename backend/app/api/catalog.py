"""
Endpoints de CRUD para cadastros base (categorias, subcategorias, instituições, cartões, tipos de investimento).
"""
from __future__ import annotations

from typing import Optional

from flask import Blueprint, jsonify, request

from ..database import get_session
from ..services.catalog_service import CatalogService

catalog_bp = Blueprint("catalog", __name__, url_prefix="/api/catalog")


def get_catalog_service() -> CatalogService:
    return CatalogService(get_session)


def _bool_arg(name: str) -> bool:
    value = request.args.get(name)
    if value is None:
        return False
    return str(value).lower() in {"1", "true", "yes", "on"}


def _optional_bool(value: Optional[object]) -> Optional[bool]:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return bool(value)


def _optional_int(value: Optional[object]) -> Optional[int]:
    if value is None:
        return None
    return int(value)


def _optional_float(value: Optional[object]) -> Optional[float]:
    if value is None:
        return None
    return float(value)


# --- Categorias / Subcategorias ---
@catalog_bp.get("/categories")
def list_categories():
    service = get_catalog_service()
    items = service.list_categories(
        category_type=request.args.get("type"),
        parent_id=request.args.get("parent_id", type=int),
        include_inactive=_bool_arg("include_inactive"),
    )
    return jsonify({"items": items})


@catalog_bp.post("/categories")
def create_category():
    data = request.get_json(silent=True) or {}
    name = data.get("name")
    category_type = data.get("type")
    if not name or not category_type:
        return jsonify({"error": "Campos 'name' e 'type' são obrigatórios."}), 400

    parent_id = data.get("parent_id")
    if parent_id is not None:
        try:
            parent_id = int(parent_id)
        except (TypeError, ValueError):
            return jsonify({"error": "parent_id deve ser numérico."}), 400

    service = get_catalog_service()
    try:
        created = service.create_category(
            name=name,
            category_type=category_type,
            user_id=int(data.get("user_id") or 1),
            parent_id=parent_id,
            color=data.get("color"),
            icon=data.get("icon"),
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(created), 201


@catalog_bp.get("/categories/<int:category_id>")
def get_category(category_id: int):
    service = get_catalog_service()
    category = service.get_category(category_id)
    if not category:
        return jsonify({"error": "Categoria não encontrada"}), 404
    return jsonify(category)


@catalog_bp.put("/categories/<int:category_id>")
def update_category(category_id: int):
    data = request.get_json(silent=True) or {}
    parent_id = data.get("parent_id")
    if parent_id is not None:
        try:
            parent_id = int(parent_id)
        except (TypeError, ValueError):
            return jsonify({"error": "parent_id deve ser numérico."}), 400

    service = get_catalog_service()
    try:
        updated = service.update_category(
            category_id,
            name=data.get("name"),
            category_type=data.get("type"),
            parent_id=parent_id,
            color=data.get("color"),
            icon=data.get("icon"),
            is_active=_optional_bool(data.get("is_active")),
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    if not updated:
        return jsonify({"error": "Categoria não encontrada"}), 404
    return jsonify(updated)


@catalog_bp.delete("/categories/<int:category_id>")
def delete_category(category_id: int):
    service = get_catalog_service()
    try:
        deleted = service.delete_category(category_id)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    if not deleted:
        return jsonify({"error": "Categoria não encontrada"}), 404
    return ("", 204)


# --- Instituições ---
@catalog_bp.get("/institutions")
def list_institutions():
    service = get_catalog_service()
    items = service.list_institutions(include_inactive=_bool_arg("include_inactive"))
    return jsonify({"items": items})


@catalog_bp.post("/institutions")
def create_institution():
    data = request.get_json(silent=True) or {}
    name = data.get("name")
    account_type = data.get("account_type")
    if not name or not account_type:
        return jsonify({"error": "Campos 'name' e 'account_type' são obrigatórios."}), 400

    try:
        initial_balance = _optional_float(data.get("initial_balance")) or 0.0
        current_balance = _optional_float(data.get("current_balance"))
    except (TypeError, ValueError):
        return jsonify({"error": "Valores de saldo devem ser numéricos."}), 400

    service = get_catalog_service()
    try:
        created = service.create_institution(
            name=name,
            account_type=account_type,
            user_id=int(data.get("user_id") or 1),
            partition=data.get("partition"),
            initial_balance=initial_balance,
            current_balance=current_balance,
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(created), 201


@catalog_bp.put("/institutions/<int:institution_id>")
def update_institution(institution_id: int):
    data = request.get_json(silent=True) or {}
    try:
        initial_balance = _optional_float(data.get("initial_balance"))
        current_balance = _optional_float(data.get("current_balance"))
    except (TypeError, ValueError):
        return jsonify({"error": "Valores de saldo devem ser numéricos."}), 400

    service = get_catalog_service()
    try:
        updated = service.update_institution(
            institution_id,
            name=data.get("name"),
            account_type=data.get("account_type"),
            partition=data.get("partition"),
            initial_balance=initial_balance,
            current_balance=current_balance,
            is_active=_optional_bool(data.get("is_active")),
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    if not updated:
        return jsonify({"error": "Instituição não encontrada"}), 404
    return jsonify(updated)


@catalog_bp.delete("/institutions/<int:institution_id>")
def delete_institution(institution_id: int):
    service = get_catalog_service()
    deleted = service.delete_institution(institution_id)
    if not deleted:
        return jsonify({"error": "Instituição não encontrada"}), 404
    return ("", 204)


# --- Cartões ---
@catalog_bp.get("/credit-cards")
def list_credit_cards():
    service = get_catalog_service()
    items = service.list_credit_cards(
        include_inactive=_bool_arg("include_inactive"),
        institution_id=request.args.get("institution_id", type=int),
    )
    return jsonify({"items": items})


@catalog_bp.post("/credit-cards")
def create_credit_card():
    data = request.get_json(silent=True) or {}
    name = data.get("name")
    institution_id = data.get("institution_id")
    if not name or not institution_id:
        return jsonify({"error": "Campos 'name' e 'institution_id' são obrigatórios."}), 400

    try:
        institution_id = int(institution_id)
        closing_day = _optional_int(data.get("closing_day"))
        due_day = _optional_int(data.get("due_day"))
        limit_amount = _optional_float(data.get("limit_amount"))
    except (TypeError, ValueError):
        return jsonify({"error": "Campos numéricos inválidos para cartão."}), 400

    service = get_catalog_service()
    try:
        created = service.create_credit_card(
            name=name,
            institution_id=institution_id,
            user_id=int(data.get("user_id") or 1),
            brand=data.get("brand"),
            last_four_digits=data.get("last_four_digits"),
            closing_day=closing_day,
            due_day=due_day,
            limit_amount=limit_amount,
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(created), 201


@catalog_bp.put("/credit-cards/<int:card_id>")
def update_credit_card(card_id: int):
    data = request.get_json(silent=True) or {}
    try:
        closing_day = _optional_int(data.get("closing_day"))
        due_day = _optional_int(data.get("due_day"))
        limit_amount = _optional_float(data.get("limit_amount"))
        institution_id = _optional_int(data.get("institution_id"))
    except (TypeError, ValueError):
        return jsonify({"error": "Campos numéricos inválidos para cartão."}), 400

    service = get_catalog_service()
    try:
        updated = service.update_credit_card(
            card_id,
            name=data.get("name"),
            brand=data.get("brand"),
            last_four_digits=data.get("last_four_digits"),
            closing_day=closing_day,
            due_day=due_day,
            limit_amount=limit_amount,
            is_active=_optional_bool(data.get("is_active")),
            institution_id=institution_id,
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    if not updated:
        return jsonify({"error": "Cartão não encontrado"}), 404
    return jsonify(updated)


@catalog_bp.delete("/credit-cards/<int:card_id>")
def delete_credit_card(card_id: int):
    service = get_catalog_service()
    deleted = service.delete_credit_card(card_id)
    if not deleted:
        return jsonify({"error": "Cartão não encontrado"}), 404
    return ("", 204)


# --- Tipos de investimento ---
@catalog_bp.get("/investment-types")
def list_investment_types():
    service = get_catalog_service()
    return jsonify({"items": service.list_investment_types()})


@catalog_bp.post("/investment-types")
def create_investment_type():
    data = request.get_json(silent=True) or {}
    name = data.get("name")
    if not name:
        return jsonify({"error": "Campo 'name' é obrigatório."}), 400

    service = get_catalog_service()
    try:
        created = service.create_investment_type(
            name=name,
            classification=data.get("classification"),
            description=data.get("description"),
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify(created), 201


@catalog_bp.put("/investment-types/<int:item_id>")
def update_investment_type(item_id: int):
    data = request.get_json(silent=True) or {}
    service = get_catalog_service()
    try:
        updated = service.update_investment_type(
            item_id,
            name=data.get("name"),
            classification=data.get("classification"),
            description=data.get("description"),
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    if not updated:
        return jsonify({"error": "Tipo de investimento não encontrado"}), 404
    return jsonify(updated)


@catalog_bp.delete("/investment-types/<int:item_id>")
def delete_investment_type(item_id: int):
    service = get_catalog_service()
    deleted = service.delete_investment_type(item_id)
    if not deleted:
        return jsonify({"error": "Tipo de investimento não encontrado"}), 404
    return ("", 204)
