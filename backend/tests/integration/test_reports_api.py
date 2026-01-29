from datetime import datetime, timedelta

import pytest

from app import create_app
from app.database import get_engine, remove_session
from app.models import Base, PendingTransaction, ReviewStatus


@pytest.fixture(scope="function")
def app():
    app = create_app("testing")
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    yield app
    Base.metadata.drop_all(bind=engine)
    remove_session()


@pytest.fixture()
def client(app):
    return app.test_client()


def _make_tx(session, amount, days_ago, category, status=ReviewStatus.APPROVED):
    tx = PendingTransaction(
        import_batch_id=1,
        fitid=f"{amount}-{days_ago}-{category}",
        date=datetime.utcnow() - timedelta(days=days_ago),
        description="teste",
        amount=amount,
        transaction_type="credito" if amount >= 0 else "debito",
        predicted_category=category,
        review_status=status,
    )
    session.add(tx)
    session.commit()


def test_summary_filters_pending(client):
    from app.database import get_session

    session = get_session()
    _make_tx(session, 1000, 2, "Salário", ReviewStatus.APPROVED)
    _make_tx(session, -200, 1, "Mercado", ReviewStatus.PENDING)

    resp = client.get("/api/reports/summary")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["totals"]["income"] == 1000
    assert data["totals"]["expense"] == 0  # pendente não entra por padrão

    resp_pending = client.get("/api/reports/summary?include_pending=1")
    data_pending = resp_pending.get_json()
    assert data_pending["totals"]["expense"] == 200
    assert data_pending["count"] == 2


def test_monthly_series(client):
    from app.database import get_session

    session = get_session()
    _make_tx(session, 500, 15, "Freela", ReviewStatus.APPROVED)
    _make_tx(session, -100, 15, "Mercado", ReviewStatus.APPROVED)
    _make_tx(session, 300, 45, "Bonus", ReviewStatus.APPROVED)

    resp = client.get("/api/reports/monthly?months=2")
    assert resp.status_code == 200
    data = resp.get_json()["series"]
    # Deve trazer 2 entradas (meses mais recentes com movimento)
    assert len(data) == 2
    last = data[-1]
    assert last["income"] > 0
    assert "balance" in last
