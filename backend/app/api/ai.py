"""
Endpoints para consultor financeiro com IA (ChatGPT).
"""
from __future__ import annotations

import asyncio
from typing import Dict, Optional

from flask import Blueprint, current_app, jsonify, request
from openai import OpenAIError

from ..database import get_session
from ..models import PendingTransaction, ReviewStatus
from ..services.openai_service import OpenAIService

ai_bp = Blueprint("ai", __name__, url_prefix="/api/ai")


def get_ai_service() -> Optional[OpenAIService]:
    """
    Factory para criar OpenAIService.

    Returns:
        OpenAIService ou None se não configurado
    """
    api_key = current_app.config.get("OPENAI_API_KEY", "")

    if not api_key:
        return None

    model = current_app.config.get("OPENAI_MODEL", "gpt-3.5-turbo")
    max_tokens = current_app.config.get("OPENAI_MAX_TOKENS", 1000)

    return OpenAIService(
        api_key=api_key,
        model=model,
        max_tokens=max_tokens
    )


def _run_async(coro):
    """Helper para rodar funções async em rotas Flask."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@ai_bp.get("/health")
def health_check():
    """
    Verifica se API OpenAI está configurada e funcionando.

    Returns:
        JSON com status da API
    """
    service = get_ai_service()

    if not service:
        return jsonify({
            "configured": False,
            "message": "OPENAI_API_KEY não configurada"
        }), 200

    try:
        is_healthy = _run_async(service.health_check())

        return jsonify({
            "configured": True,
            "healthy": is_healthy,
            "model": service.model
        }), 200

    except Exception as e:
        current_app.logger.exception("Erro no health check da IA")
        return jsonify({
            "configured": True,
            "healthy": False,
            "error": str(e)
        }), 200


@ai_bp.post("/analyze")
def analyze_spending():
    """
    Analisa gastos do usuário e sugere melhorias.

    Payload:
        {
            "summary": {
                "total_income": 5000.00,
                "total_expense": 4200.00,
                "balance": 800.00,
                "top_categories": [
                    {"name": "Alimentação", "total": 1200.00},
                    {"name": "Transporte", "total": 800.00}
                ]
            },
            "timeframe": "last_month"  # opcional
        }

    Returns:
        JSON com análise e sugestões
    """
    service = get_ai_service()
    if not service:
        return jsonify({"error": "API OpenAI não configurada"}), 503

    data = request.get_json(force=True, silent=True) or {}

    summary = data.get("summary")
    timeframe = data.get("timeframe", "last_month")

    if not summary:
        return jsonify({"error": "summary é obrigatório"}), 400

    try:
        analysis = _run_async(
            service.analyze_spending(summary, timeframe)
        )

        return jsonify({
            "analysis": analysis,
            "timeframe": timeframe
        }), 200

    except OpenAIError as e:
        current_app.logger.exception("Erro na API OpenAI")
        return jsonify({
            "error": "Erro ao comunicar com API OpenAI",
            "details": str(e)
        }), 503
    except Exception as e:
        current_app.logger.exception("Erro na análise de gastos")
        return jsonify({"error": str(e)}), 500


@ai_bp.post("/chat")
def chat():
    """
    Chat interativo sobre finanças com contexto do usuário.

    Payload:
        {
            "message": "Como posso economizar mais?",
            "context": {
                "current_balance": 1500.00,
                "monthly_income": 5000.00,
                "monthly_expense": 3500.00
            }
        }

    Returns:
        JSON com resposta contextualizada
    """
    service = get_ai_service()
    if not service:
        return jsonify({"error": "API OpenAI não configurada"}), 503

    data = request.get_json(force=True, silent=True) or {}

    message = data.get("message")
    context = data.get("context", {})

    if not message:
        return jsonify({"error": "message é obrigatório"}), 400

    try:
        response = _run_async(
            service.chat_with_context(message, context)
        )

        return jsonify({
            "response": response,
            "message": message
        }), 200

    except OpenAIError as e:
        current_app.logger.exception("Erro na API OpenAI")
        return jsonify({
            "error": "Erro ao comunicar com API OpenAI",
            "details": str(e)
        }), 503
    except Exception as e:
        current_app.logger.exception("Erro no chat IA")
        return jsonify({"error": str(e)}), 500


@ai_bp.get("/insights")
def get_insights():
    """
    Gera insights sobre padrões de categorização.

    Query params:
        user_id: ID do usuário (opcional, padrão: 1)
        limit: Quantidade de transações a analisar (opcional, padrão: 50)

    Returns:
        JSON com insights sobre gastos
    """
    service = get_ai_service()
    if not service:
        return jsonify({"error": "API OpenAI não configurada"}), 503

    user_id = request.args.get("user_id", 1, type=int)
    limit = request.args.get("limit", 50, type=int)

    session = get_session()

    try:
        # Buscar transações aprovadas recentes
        query = session.query(PendingTransaction).filter(
            PendingTransaction.review_status.in_([
                ReviewStatus.APPROVED,
                ReviewStatus.MODIFIED
            ])
        ).order_by(PendingTransaction.date.desc()).limit(limit)

        transactions = query.all()

        if not transactions:
            return jsonify({
                "message": "Nenhuma transação aprovada encontrada",
                "insights": None
            }), 200

        # Converter para formato para IA
        tx_list = []
        categories_dict = {}

        for tx in transactions:
            category = tx.final_category or "Sem categoria"

            tx_list.append({
                "date": tx.date.isoformat() if tx.date else None,
                "description": tx.description,
                "amount": float(tx.amount) if tx.amount else 0.0,
                "category": category
            })

            # Agregar por categoria
            if category not in categories_dict:
                categories_dict[category] = {"count": 0, "total": 0.0}

            categories_dict[category]["count"] += 1
            categories_dict[category]["total"] += float(tx.amount) if tx.amount else 0.0

        # Converter dict para lista
        categories_list = [
            {"name": name, **stats}
            for name, stats in categories_dict.items()
        ]

        # Gerar insights
        insights = _run_async(
            service.generate_insights(categories_list, tx_list[:10])
        )

        return jsonify({
            "insights": insights,
            "analyzed_transactions": len(tx_list),
            "categories_count": len(categories_list)
        }), 200

    except OpenAIError as e:
        current_app.logger.exception("Erro na API OpenAI")
        return jsonify({
            "error": "Erro ao comunicar com API OpenAI",
            "details": str(e)
        }), 503
    except Exception as e:
        current_app.logger.exception("Erro ao gerar insights")
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


@ai_bp.post("/projections")
def create_projections():
    """
    Cria projeções financeiras e plano para atingir metas.

    Payload:
        {
            "goals": {
                "savings_target": 10000.00,
                "target_date": "2024-12-31",
                "purpose": "Emergência"
            },
            "current_state": {
                "current_savings": 2000.00,
                "monthly_income": 5000.00,
                "monthly_expense": 3500.00
            }
        }

    Returns:
        JSON com projeções e plano de ação
    """
    service = get_ai_service()
    if not service:
        return jsonify({"error": "API OpenAI não configurada"}), 503

    data = request.get_json(force=True, silent=True) or {}

    goals = data.get("goals")
    current_state = data.get("current_state")

    if not goals or not current_state:
        return jsonify({"error": "goals e current_state são obrigatórios"}), 400

    try:
        projections = _run_async(
            service.create_projections(goals, current_state)
        )

        return jsonify({
            "projections": projections,
            "goals": goals
        }), 200

    except OpenAIError as e:
        current_app.logger.exception("Erro na API OpenAI")
        return jsonify({
            "error": "Erro ao comunicar com API OpenAI",
            "details": str(e)
        }), 503
    except Exception as e:
        current_app.logger.exception("Erro ao criar projeções")
        return jsonify({"error": str(e)}), 500
