"""
Endpoints para treinamento de modelos ML.
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Optional

from flask import Blueprint, current_app, jsonify, request
from werkzeug.utils import secure_filename

from ..database import get_session
from ..services.training_service import TrainingService

training_bp = Blueprint("training", __name__, url_prefix="/api/training")


def get_training_service() -> TrainingService:
    """Factory para criar TrainingService."""
    models_folder = current_app.config.get("ML_MODELS_FOLDER", "app/ml/models")
    upload_folder = current_app.config.get("UPLOAD_FOLDER", "uploads")

    return TrainingService(
        session_factory=get_session,
        models_folder=models_folder,
        upload_folder=upload_folder
    )


def _allowed_file(filename: str) -> bool:
    """Verifica se arquivo CSV é permitido."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() == "csv"


@training_bp.post("/upload-csv")
def upload_csv():
    """
    Upload de arquivo CSV para treinamento.

    Returns:
        JSON com info do arquivo e preview
    """
    if "file" not in request.files:
        return jsonify({"error": "Arquivo não enviado"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Nome do arquivo inválido"}), 400

    if not _allowed_file(file.filename):
        return jsonify({"error": "Apenas arquivos CSV são permitidos"}), 400

    # Salvar arquivo
    safe_name = secure_filename(file.filename)
    upload_dir = Path(current_app.config["UPLOAD_FOLDER"])
    upload_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    stored_name = f"training_{timestamp}_{safe_name}"
    stored_path = upload_dir / stored_name

    file.save(stored_path)

    # Validar CSV
    service = get_training_service()
    is_valid, errors = service.validate_csv(str(stored_path))

    if not is_valid:
        # Remover arquivo inválido
        stored_path.unlink()
        return jsonify({
            "error": "CSV inválido",
            "details": errors
        }), 400

    # Gerar preview
    try:
        preview = service.preview_csv(str(stored_path))

        return jsonify({
            "csv_id": stored_name,
            "csv_path": str(stored_path),
            "valid": True,
            "preview": preview
        }), 201

    except Exception as e:
        current_app.logger.exception("Erro ao processar CSV")
        stored_path.unlink()  # Limpar arquivo
        return jsonify({"error": f"Erro ao processar CSV: {str(e)}"}), 500


@training_bp.post("/train")
def train_model():
    """
    Inicia treinamento de modelo com CSV uploadado.

    Payload:
        {
            "csv_id": "training_20240101_data.csv",
            "user_id": 1  # TODO: pegar do JWT
        }

    Returns:
        JSON com info do job iniciado
    """
    data = request.get_json(force=True, silent=True) or {}

    csv_id = data.get("csv_id")
    user_id = data.get("user_id", 1)  # TODO: Get from JWT token

    if not csv_id:
        return jsonify({"error": "csv_id é obrigatório"}), 400

    # Verificar se arquivo existe
    upload_dir = Path(current_app.config["UPLOAD_FOLDER"])
    csv_path = upload_dir / csv_id

    if not csv_path.exists():
        return jsonify({"error": "Arquivo CSV não encontrado"}), 404

    # Preparar dados e treinar
    service = get_training_service()

    try:
        df = service.prepare_training_data(str(csv_path))

        # Treinar modelo (síncrono por enquanto - pode ser async com Celery depois)
        from ..models import TrainingJobSource
        result = service.train_model(
            data=df,
            user_id=user_id,
            source=TrainingJobSource.CSV_UPLOAD,
            csv_path=str(csv_path)
        )

        return jsonify(result), 201

    except Exception as e:
        current_app.logger.exception("Erro ao treinar modelo")
        return jsonify({
            "error": "Erro ao treinar modelo",
            "details": str(e)
        }), 500


@training_bp.get("/status/<int:job_id>")
def get_job_status(job_id: int):
    """
    Retorna status de um job de treinamento.

    Args:
        job_id: ID do job

    Returns:
        JSON com status do job
    """
    service = get_training_service()
    job = service.get_job_status(job_id)

    if not job:
        return jsonify({"error": "Job não encontrado"}), 404

    return jsonify(job), 200


@training_bp.get("/history")
def get_training_history():
    """
    Lista histórico de treinamentos.

    Query params:
        user_id: Filtrar por usuário (opcional)
        limit: Máximo de resultados (padrão: 20)

    Returns:
        JSON com lista de jobs
    """
    user_id = request.args.get("user_id", type=int)
    limit = request.args.get("limit", 20, type=int)

    service = get_training_service()
    history = service.list_training_history(user_id=user_id, limit=limit)

    return jsonify({"jobs": history, "count": len(history)}), 200


@training_bp.post("/auto-retrain")
def trigger_auto_retrain():
    """
    Inicia retreinamento automático com transações aprovadas.

    Payload:
        {
            "user_id": 1,  # TODO: pegar do JWT
            "min_transactions": 100  # opcional
        }

    Returns:
        JSON com resultado do treinamento ou aviso de dados insuficientes
    """
    data = request.get_json(force=True, silent=True) or {}

    user_id = data.get("user_id", 1)  # TODO: Get from JWT token
    min_transactions = data.get("min_transactions", 100)

    service = get_training_service()

    try:
        result = service.auto_retrain_from_approved(
            user_id=user_id,
            min_transactions=min_transactions
        )

        if result is None:
            return jsonify({
                "message": "Dados insuficientes para retreinamento",
                "min_required": min_transactions
            }), 200

        return jsonify(result), 201

    except Exception as e:
        current_app.logger.exception("Erro no auto-retreinamento")
        return jsonify({
            "error": "Erro no auto-retreinamento",
            "details": str(e)
        }), 500


@training_bp.post("/activate")
def activate_model():
    """
    Ativa um modelo treinado (substitui o modelo em uso).

    Payload:
        {
            "model_version": "20240101_120000"
        }

    Returns:
        JSON confirmando ativação
    """
    data = request.get_json(force=True, silent=True) or {}

    model_version = data.get("model_version")

    if not model_version:
        return jsonify({"error": "model_version é obrigatório"}), 400

    service = get_training_service()

    try:
        success = service.activate_model(model_version)

        if success:
            return jsonify({
                "message": "Modelo ativado com sucesso",
                "model_version": model_version,
                "note": "Reinicie a aplicação para carregar o novo modelo"
            }), 200
        else:
            return jsonify({"error": "Falha ao ativar modelo"}), 500

    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        current_app.logger.exception("Erro ao ativar modelo")
        return jsonify({
            "error": "Erro ao ativar modelo",
            "details": str(e)
        }), 500
