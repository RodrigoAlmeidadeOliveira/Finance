import pytest

from app import create_app
from app.database import get_engine, remove_session
from app.models import Base


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


def test_category_and_subcategory_crud(client):
    # Criar categoria raiz
    resp = client.post(
        "/api/catalog/categories",
        json={"name": "Alimentação", "type": "expense", "color": "#ff0000"},
    )
    assert resp.status_code == 201
    category = resp.get_json()
    category_id = category["id"]

    # Criar subcategoria herdando tipo do pai
    resp_sub = client.post(
        "/api/catalog/categories",
        json={"name": "Supermercado", "type": "expense", "parent_id": category_id},
    )
    assert resp_sub.status_code == 201
    subcategory_id = resp_sub.get_json()["id"]

    # Listar subcategorias por parent_id
    list_resp = client.get(f"/api/catalog/categories?parent_id={category_id}")
    assert list_resp.status_code == 200
    assert any(item["id"] == subcategory_id for item in list_resp.get_json()["items"])

    # Atualizar categoria
    update_resp = client.put(
        f"/api/catalog/categories/{category_id}",
        json={"name": "Alimentação e Bebidas", "color": "#00ff00"},
    )
    assert update_resp.status_code == 200
    assert update_resp.get_json()["name"] == "Alimentação e Bebidas"

    # Impedir exclusão com filhos
    delete_resp = client.delete(f"/api/catalog/categories/{category_id}")
    assert delete_resp.status_code == 400

    # Remover filho e depois pai
    resp = client.delete(f"/api/catalog/categories/{subcategory_id}")
    assert resp.status_code == 204
    resp = client.delete(f"/api/catalog/categories/{category_id}")
    assert resp.status_code == 204


def test_institution_and_card_crud(client):
    resp_inst = client.post(
        "/api/catalog/institutions",
        json={
            "name": "Banco do Teste",
            "account_type": "corrente",
            "partition": "principal",
            "initial_balance": 1000.0,
        },
    )
    assert resp_inst.status_code == 201
    institution_id = resp_inst.get_json()["id"]

    list_resp = client.get("/api/catalog/institutions")
    assert list_resp.status_code == 200
    assert any(item["id"] == institution_id for item in list_resp.get_json()["items"])

    # Criar cartão vinculado
    resp_card = client.post(
        "/api/catalog/credit-cards",
        json={
            "name": "Cartão Teste",
            "institution_id": institution_id,
            "brand": "Visa",
            "closing_day": 10,
            "due_day": 20,
            "limit_amount": 5000,
        },
    )
    assert resp_card.status_code == 201
    card_id = resp_card.get_json()["id"]

    # Atualizar cartão
    resp_update = client.put(
        f"/api/catalog/credit-cards/{card_id}",
        json={"limit_amount": 7500, "due_day": 22},
    )
    assert resp_update.status_code == 200
    payload = resp_update.get_json()
    assert payload["limit_amount"] == 7500
    assert payload["due_day"] == 22

    # Filtrar cartões por instituição
    list_cards = client.get(f"/api/catalog/credit-cards?institution_id={institution_id}")
    assert list_cards.status_code == 200
    assert any(item["id"] == card_id for item in list_cards.get_json()["items"])

    # Remover cartão e instituição
    assert client.delete(f"/api/catalog/credit-cards/{card_id}").status_code == 204
    assert client.delete(f"/api/catalog/institutions/{institution_id}").status_code == 204


def test_investment_type_crud_and_duplicates(client):
    resp = client.post(
        "/api/catalog/investment-types",
        json={"name": "CDB", "classification": "renda_fixa"},
    )
    assert resp.status_code == 201
    item_id = resp.get_json()["id"]

    # Duplicado não permitido
    duplicate = client.post(
        "/api/catalog/investment-types",
        json={"name": "CDB"},
    )
    assert duplicate.status_code == 400

    # Atualizar item
    update = client.put(
        f"/api/catalog/investment-types/{item_id}",
        json={"name": "ETF", "classification": "renda_variavel"},
    )
    assert update.status_code == 200
    assert update.get_json()["name"] == "ETF"

    # Listar
    list_resp = client.get("/api/catalog/investment-types")
    assert list_resp.status_code == 200
    assert any(item["name"] == "ETF" for item in list_resp.get_json()["items"])

    # Remover
    assert client.delete(f"/api/catalog/investment-types/{item_id}").status_code == 204
