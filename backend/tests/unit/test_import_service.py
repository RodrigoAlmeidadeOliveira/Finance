from pathlib import Path

from app.database import init_engine, get_session, remove_session
from app.importers import OFXImporter
from app.models import Base
from app.services.import_service import ImportService


class DummyPredictor:
    """
    Preditor fake para testes unitários.
    """

    def predict_batch(self, descriptions, values, transaction_types, dates):
        return [
            {
                "category": "Teste",
                "confidence": 0.95,
                "confidence_level": "high",
                "suggestions": [],
            }
            for _ in descriptions
        ]


def setup_module():
    engine = init_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)


def teardown_module():
    remove_session()


def test_import_service_creates_batch_and_pending(tmp_path):
    ofx_path = Path(__file__).resolve().parents[3] / "OFX" / "extrato_BB_NOV_25.ofx"
    assert ofx_path.exists(), "Arquivo OFX de teste não encontrado"

    predictor = DummyPredictor()
    service = ImportService(get_session, predictor, upload_folder=str(tmp_path))

    result = service.import_ofx_file(str(ofx_path), ofx_path.name, user_id=1)

    assert result["batch"]["filename"] == ofx_path.name
    assert result["batch"]["total_transactions"] == len(result["pending_transactions"])
    assert result["duplicates_skipped"] == []
    assert result["summary"]["transactions"]["total"] == len(result["pending_transactions"])
