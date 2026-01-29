"""
Endpoints relacionados ao modelo de Machine Learning.
"""
from flask import Blueprint, current_app, jsonify

ml_bp = Blueprint("ml", __name__, url_prefix="/api/ml")


@ml_bp.get("/stats")
def get_ml_stats():
    """
    Retorna estatísticas do modelo de ML.

    Returns:
        JSON com informações do modelo:
        - accuracy: Acurácia do modelo (se disponível)
        - n_categories: Número de categorias
        - categories: Lista de categorias
        - is_loaded: Se o modelo está carregado
        - training_metrics: Métricas de treinamento (se disponíveis)
    """
    predictor = current_app.extensions.get("predictor")

    if not predictor:
        return jsonify({
            "is_loaded": False,
            "accuracy": 0.0,
            "n_categories": 0,
            "categories": [],
            "message": "Modelo ML não está carregado"
        }), 200

    try:
        model_info = predictor.get_model_info()
        training_metrics = model_info.get("training_metrics", {})

        # Extrair acurácia das métricas de treinamento
        accuracy = training_metrics.get("accuracy", 0.0)

        return jsonify({
            "is_loaded": True,
            "accuracy": float(accuracy),
            "n_categories": model_info["n_categories"],
            "categories": model_info["categories"],
            "n_features": model_info.get("n_features", 0),
            "training_metrics": training_metrics
        }), 200

    except Exception as exc:
        current_app.logger.exception("Erro ao obter estatísticas do modelo ML")
        return jsonify({
            "error": "Erro ao obter estatísticas do modelo",
            "details": str(exc)
        }), 500


@ml_bp.get("/health")
def ml_health():
    """
    Verifica se o modelo ML está carregado e funcionando.

    Returns:
        JSON com status do modelo
    """
    predictor = current_app.extensions.get("predictor")

    return jsonify({
        "status": "healthy" if predictor else "unavailable",
        "is_loaded": predictor is not None
    }), 200
