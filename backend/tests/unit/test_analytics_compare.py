from datetime import datetime, timedelta

from app.database import get_engine, get_session, init_engine, remove_session
from app.models import Base, PendingTransaction, ReviewStatus
from app.services.analytics_service import AnalyticsService


def setup_function():
    init_engine("sqlite:///:memory:")
    engine = get_engine()
    Base.metadata.create_all(bind=engine)


def teardown_function():
    engine = get_engine()
    Base.metadata.drop_all(bind=engine)
    remove_session()


def test_compare_periods():
    from app.database import get_session

    session = get_session()
    today = datetime.utcnow()
    prev = today - timedelta(days=30)
    txs = [
        PendingTransaction(
          import_batch_id=None,
          fitid="1",
          date=today,
          description="Salario",
          amount=1000.0,
          transaction_type="credito",
          review_status=ReviewStatus.APPROVED,
        ),
        PendingTransaction(
          import_batch_id=None,
          fitid="2",
          date=today,
          description="Mercado",
          amount=-400.0,
          transaction_type="debito",
          review_status=ReviewStatus.APPROVED,
        ),
        PendingTransaction(
          import_batch_id=None,
          fitid="3",
          date=prev,
          description="Salario",
          amount=900.0,
          transaction_type="credito",
          review_status=ReviewStatus.APPROVED,
        ),
        PendingTransaction(
          import_batch_id=None,
          fitid="4",
          date=prev,
          description="Conta",
          amount=-300.0,
          transaction_type="debito",
          review_status=ReviewStatus.APPROVED,
        ),
    ]
    session.add_all(txs)
    session.commit()

    service = AnalyticsService(get_session)
    result = service.compare_periods(
        start=prev.isoformat(),
        end=today.isoformat(),
        include_pending=False,
    )

    assert result["current"]["totals"]["income"] == 1900.0
    assert result["previous"]["totals"]["income"] == 0.0
    assert result["deltas"]["balance"] == result["current"]["totals"]["balance"] - result["previous"]["totals"]["balance"]
