from datetime import datetime

import pytest

from app.database import get_engine, init_engine, remove_session
from app.models import Base, ImportBatch, PendingTransaction, ReviewStatus
from app.services.catalog_seed import CatalogSeeder


@pytest.fixture(scope="function")
def session():
    init_engine("sqlite:///:memory:")
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    from app.database import get_session

    yield get_session()

    Base.metadata.drop_all(bind=engine)
    remove_session()


def _create_import(session):
    batch = ImportBatch(
        user_id=1,
        filename="test.ofx",
        status="review",
        institution_name="Banco Teste",
        account_id="123",
        balance=250.0,
        period_start=datetime.utcnow(),
        period_end=datetime.utcnow(),
    )
    session.add(batch)
    session.flush()

    tx1 = PendingTransaction(
        import_batch_id=batch.id,
        fitid="1",
        date=datetime.utcnow(),
        description="Mercado",
        amount=-120.0,
        transaction_type="debito",
        predicted_category="Supermercado",
        review_status=ReviewStatus.PENDING,
    )
    tx2 = PendingTransaction(
        import_batch_id=batch.id,
        fitid="2",
        date=datetime.utcnow(),
        description="Salario",
        amount=5000.0,
        transaction_type="credito",
        predicted_category="Salário",
        review_status=ReviewStatus.PENDING,
    )
    session.add_all([tx1, tx2])
    session.commit()


def test_seed_creates_categories_and_institutions(session):
    _create_import(session)

    seeder = CatalogSeeder(lambda: session)
    result = seeder.seed_from_imports()

    assert result["institutions_created"] == 1
    assert result["categories_created"] == 2

    # Rodar novamente não deve criar duplicados
    result2 = seeder.seed_from_imports()
    assert result2["institutions_created"] == 0
    assert result2["categories_created"] == 0
