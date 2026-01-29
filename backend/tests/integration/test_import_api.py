import io
from pathlib import Path
import pytest

from app import create_app
from app.database import get_engine, remove_session
from app.models import Base, ReviewStatus


class DummyPredictor:
    """Preditor fake para evitar carregar modelo real em testes."""

    def predict_batch(self, descriptions, values, transaction_types, dates):
        return [
            {
                "category": "Teste",
                "confidence": 0.9,
                "confidence_level": "high",
                "suggestions": [{"category": "Teste", "probability": 0.9}],
            }
            for _ in descriptions
        ]


@pytest.fixture(scope="function")
def app(tmp_path):
    app = create_app("testing")
    app.config["UPLOAD_FOLDER"] = str(tmp_path)
    # Substituir o modelo pesado por um fake mais rápido
    app.extensions["predictor"] = DummyPredictor()

    # Criar tabelas em memória
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    yield app

    # Teardown
    Base.metadata.drop_all(bind=engine)
    remove_session()


@pytest.fixture()
def client(app):
    return app.test_client()


def test_import_ofx_and_review_flow(client):
    ofx_path = Path(__file__).resolve().parents[3] / "OFX" / "extrato_BB_NOV_25.ofx"
    assert ofx_path.exists(), "Arquivo OFX de teste não encontrado"

    # Upload OFX
    with open(ofx_path, "rb") as fh:
        resp = client.post(
            "/api/imports/ofx",
            data={
                "file": (io.BytesIO(fh.read()), ofx_path.name),
                "user_id": "1",
            },
            content_type="multipart/form-data",
        )

    assert resp.status_code == 201
    data = resp.get_json()
    batch_id = data["batch"]["id"]
    assert data["pending_transactions"], "Deve criar transações pendentes"

    # Listar lotes
    resp_list = client.get("/api/imports")
    assert resp_list.status_code == 200
    assert any(item["id"] == batch_id for item in resp_list.get_json()["items"])

    # Listar pendentes
    resp_pending = client.get(f"/api/imports/{batch_id}/pending")
    assert resp_pending.status_code == 200
    pending_items = resp_pending.get_json()["items"]
    assert pending_items

    tx_id = pending_items[0]["id"]

    # Revisar transação
    resp_review = client.post(
        f"/api/imports/{batch_id}/pending/{tx_id}/review",
        json={"category": "Categoria Final", "status": ReviewStatus.APPROVED.value},
    )
    assert resp_review.status_code == 200
    reviewed = resp_review.get_json()
    assert reviewed["review_status"] == ReviewStatus.APPROVED.value
    assert reviewed["user_category"] == "Categoria Final"
