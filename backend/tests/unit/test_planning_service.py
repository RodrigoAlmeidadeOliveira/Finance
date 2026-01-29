from datetime import date

import pytest

from app.database import get_engine, init_engine, remove_session
from app.models import Base, Institution
from app.services.planning_service import PlanningService


@pytest.fixture(scope="function")
def session():
    init_engine("sqlite:///:memory:")
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    from app.database import get_session

    yield get_session()

    Base.metadata.drop_all(bind=engine)
    remove_session()


def _seed_institution(session):
    inst = Institution(user_id=1, name="Banco Teste", account_type="corrente", initial_balance=100.0)
    session.add(inst)
    session.commit()
    return inst.id


def test_create_and_update_plan(session):
    inst_id = _seed_institution(session)
    service = PlanningService(lambda: session)

    created = service.create_plan(
        name="Aposentadoria",
        goal_amount=100000.0,
        monthly_contribution=1500.0,
        current_balance=20000.0,
        institution_id=inst_id,
        target_date=date.today().isoformat(),
    )

    assert created["name"] == "Aposentadoria"
    assert created["progress"] == 20.0

    updated = service.update_plan(
        created["id"],
        current_balance=25000.0,
        monthly_contribution=2000.0,
    )
    assert updated["current_balance"] == 25000.0
    assert updated["progress"] == 25.0


def test_income_projection_crud(session):
    service = PlanningService(lambda: session)

    item = service.create_income_projection(
        description="Salário",
        amount=5000.0,
        expected_date=date.today().isoformat(),
        projection_type="fixed",
    )
    assert item["projection_type"] == "fixed"
    assert item["received"] is False

    updated = service.update_income_projection(
        item["id"],
        received=True,
        amount=5200.0,
    )
    assert updated["received"] is True
    assert updated["amount"] == 5200.0

    listed = service.list_income_projections()
    assert len(listed) == 1

    assert service.delete_income_projection(item["id"]) is True
    assert service.list_income_projections() == []
