"""
Endpoints relacionados à importação de arquivos OFX.
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Optional

from flask import Blueprint, current_app, jsonify, request
from werkzeug.utils import secure_filename

from ..database import get_session
from ..models import ReviewStatus
from ..services.import_service import ImportService

imports_bp = Blueprint("imports", __name__, url_prefix="/api/imports")


def get_import_service() -> ImportService:
    predictor = current_app.extensions["predictor"]
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    return ImportService(get_session, predictor, upload_folder)


def _allowed_file(filename: str) -> bool:
    allowed = current_app.config.get("ALLOWED_EXTENSIONS", {"ofx"})
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed


def _parse_status(value: Optional[str]) -> ReviewStatus:
    if not value:
        return ReviewStatus.APPROVED
    for status in ReviewStatus:
        if status.value == value:
            return status
    return ReviewStatus.APPROVED


def _handle_upload():
    """
    Função auxiliar para processar upload de arquivo OFX.
    """
    if "file" not in request.files:
        return jsonify({"error": "Arquivo OFX não enviado"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Nome do arquivo inválido"}), 400

    if not _allowed_file(file.filename):
        return jsonify({"error": "Extensão não permitida"}), 400

    safe_name = secure_filename(file.filename)
    upload_dir = Path(current_app.config["UPLOAD_FOLDER"])
    upload_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    stored_name = f"{timestamp}_{safe_name}"
    stored_path = upload_dir / stored_name
    file.save(stored_path)

    user_id = int(request.form.get("user_id", 1))

    service = get_import_service()
    try:
        result = service.import_ofx_file(str(stored_path), safe_name, user_id)
    except ValueError as exc:
        current_app.logger.exception("Erro de validação no upload OFX")
        return jsonify({"error": str(exc)}), 400
    except Exception:
        current_app.logger.exception("Erro ao processar arquivo OFX")
        return jsonify({"error": "Erro interno ao processar arquivo OFX"}), 500

    return jsonify(result), 201


@imports_bp.post("/ofx")
def upload_ofx():
    """
    Upload e processamento de arquivo OFX.
    """
    return _handle_upload()


@imports_bp.post("/upload")
def upload_ofx_alt():
    """
    Upload e processamento de arquivo OFX (rota alternativa).
    """
    return _handle_upload()


@imports_bp.get("")
def list_imports():
    """
    Lista lotes de importação existentes.
    """
    service = get_import_service()
    batches = service.list_batches()
    return jsonify({"items": batches})


@imports_bp.get("/batches")
def list_batches_alt():
    """
    Lista lotes de importação existentes (rota alternativa).
    """
    service = get_import_service()
    batches = service.list_batches()
    return jsonify({"batches": batches})


@imports_bp.get("/<int:batch_id>")
def get_import(batch_id: int):
    """
    Recupera informações de um lote específico.
    """
    service = get_import_service()
    batch = service.get_batch(batch_id)
    if not batch:
        return jsonify({"error": "Lote não encontrado"}), 404
    return jsonify(batch)


@imports_bp.get("/batches/<int:batch_id>")
def get_batch_alt(batch_id: int):
    """
    Recupera informações de um lote específico (rota alternativa).
    """
    service = get_import_service()
    batch = service.get_batch(batch_id)
    if not batch:
        return jsonify({"error": "Lote não encontrado"}), 404
    return jsonify(batch)


@imports_bp.get("/<int:batch_id>/pending")
def list_pending(batch_id: int):
    """
    Lista transações pendentes de revisão de um lote.
    """
    service = get_import_service()
    pending = service.list_pending_transactions(batch_id)
    return jsonify({"items": pending})


@imports_bp.get("/batches/<int:batch_id>/transactions")
def list_transactions_alt(batch_id: int):
    """
    Lista transações pendentes de revisão de um lote (rota alternativa).
    """
    service = get_import_service()
    pending = service.list_pending_transactions(batch_id)
    return jsonify({"transactions": pending})


@imports_bp.post("/<int:batch_id>/pending/<int:transaction_id>/review")
def review_pending(batch_id: int, transaction_id: int):
    """
    Confirma ou ajusta classificação de uma transação pendente.
    """
    data = request.get_json(force=True, silent=True) or {}
    category = data.get("category")
    if not category:
        return jsonify({"error": "Campo 'category' é obrigatório"}), 400

    notes = data.get("notes")
    status = _parse_status(data.get("status"))

    service = get_import_service()
    result = service.review_transaction(
        batch_id=batch_id,
        transaction_id=transaction_id,
        final_category=category,
        status=status,
        notes=notes,
    )

    if not result:
        return jsonify({"error": "Transação não encontrada"}), 404

    return jsonify(result)


@imports_bp.route("/batches/<int:batch_id>/transactions/<int:transaction_id>", methods=["PUT", "POST"])
def review_transaction_alt(batch_id: int, transaction_id: int):
    """
    Confirma ou ajusta classificação de uma transação pendente (rota alternativa).
    """
    data = request.get_json(force=True, silent=True) or {}
    category = data.get("category")
    if not category:
        return jsonify({"error": "Campo 'category' é obrigatório"}), 400

    notes = data.get("notes")
    status = _parse_status(data.get("status"))

    service = get_import_service()
    result = service.review_transaction(
        batch_id=batch_id,
        transaction_id=transaction_id,
        final_category=category,
        status=status,
        notes=notes,
    )

    if not result:
        return jsonify({"error": "Transação não encontrada"}), 404

    return jsonify(result)


@imports_bp.delete("/batches/<int:batch_id>")
def delete_batch(batch_id: int):
    """
    Remove um lote de importação e todas as suas transações.
    """
    from flask import g

    user_id = g.get("user_id", 1)  # TODO: Get from JWT token
    service = get_import_service()

    success = service.delete_batch(batch_id, user_id)

    if not success:
        return jsonify({"error": "Lote não encontrado ou sem permissão"}), 404

    return jsonify({"message": "Lote removido com sucesso"}), 200


@imports_bp.put("/batches/<int:batch_id>")
def update_batch(batch_id: int):
    """
    Atualiza metadados de um lote de importação.
    """
    from flask import g

    user_id = g.get("user_id", 1)  # TODO: Get from JWT token
    data = request.get_json(force=True, silent=True) or {}

    service = get_import_service()
    result = service.update_batch(batch_id, user_id, **data)

    if not result:
        return jsonify({"error": "Lote não encontrado ou sem permissão"}), 404

    return jsonify(result), 200


@imports_bp.delete("/batches/<int:batch_id>/transactions/<int:transaction_id>")
def delete_transaction(batch_id: int, transaction_id: int):
    """
    Remove uma transação pendente específica.
    """
    service = get_import_service()
    success = service.delete_transaction(batch_id, transaction_id)

    if not success:
        return jsonify({"error": "Transação não encontrada"}), 404

    return jsonify({"message": "Transação removida com sucesso"}), 200


@imports_bp.get("/duplicates")
def find_duplicates():
    """
    Identifica transações potencialmente duplicadas.
    """
    threshold_days = request.args.get("threshold_days", 3, type=int)

    service = get_import_service()
    duplicates = service.find_duplicates(threshold_days)

    return jsonify({
        "duplicates": duplicates,
        "count": len(duplicates),
        "threshold_days": threshold_days
    }), 200


@imports_bp.post("/merge-duplicates")
def merge_duplicates():
    """
    Mantém uma transação e remove as duplicatas.
    """
    data = request.get_json(force=True, silent=True) or {}

    keep_id = data.get("keep_transaction_id")
    remove_ids = data.get("remove_transaction_ids", [])

    if not keep_id or not remove_ids:
        return jsonify({
            "error": "Campos 'keep_transaction_id' e 'remove_transaction_ids' são obrigatórios"
        }), 400

    service = get_import_service()
    result = service.merge_duplicates(keep_id, remove_ids)

    if not result:
        return jsonify({"error": "Transação não encontrada"}), 404

    return jsonify({
        "message": "Duplicatas removidas com sucesso",
        "kept_transaction": result,
        "removed_count": len(remove_ids)
    }), 200
