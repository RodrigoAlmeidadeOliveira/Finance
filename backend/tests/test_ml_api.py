"""
Testes para endpoints da API de Machine Learning.
"""
import pytest
from app import create_app
from app.ml import TransactionPredictor


@pytest.fixture
def app():
    """Fixture da aplicação Flask."""
    app = create_app('testing')
    return app


@pytest.fixture
def client(app):
    """Fixture do cliente de teste."""
    return app.test_client()


def test_ml_stats_without_model(client):
    """
    Testa endpoint /api/ml/stats quando modelo não está carregado.
    """
    response = client.get('/api/ml/stats')
    assert response.status_code == 200

    data = response.get_json()
    assert 'is_loaded' in data
    assert 'accuracy' in data
    assert 'n_categories' in data

    # Quando não há modelo carregado
    if not data['is_loaded']:
        assert data['accuracy'] == 0.0
        assert data['n_categories'] == 0
        assert data['categories'] == []


def test_ml_stats_with_model(app, client):
    """
    Testa endpoint /api/ml/stats quando modelo está carregado.
    """
    # Mock do predictor
    class MockPredictor:
        def get_model_info(self):
            return {
                'model_path': '/fake/path',
                'n_categories': 18,
                'categories': ['Alimentação', 'Transporte', 'Saúde'],
                'training_metrics': {
                    'test_accuracy': 0.73,
                    'train_accuracy': 0.85
                },
                'n_features': 50
            }

    # Injetar mock no app
    with app.app_context():
        app.extensions['predictor'] = MockPredictor()

        response = client.get('/api/ml/stats')
        assert response.status_code == 200

        data = response.get_json()
        assert data['is_loaded'] is True
        assert data['accuracy'] == 0.73
        assert data['n_categories'] == 18
        assert len(data['categories']) == 3
        assert 'Alimentação' in data['categories']


def test_ml_health_endpoint(client):
    """
    Testa endpoint /api/ml/health.
    """
    response = client.get('/api/ml/health')
    assert response.status_code == 200

    data = response.get_json()
    assert 'status' in data
    assert 'is_loaded' in data
    assert data['status'] in ['healthy', 'unavailable']


def test_ml_stats_error_handling(app, client):
    """
    Testa tratamento de erros no endpoint /api/ml/stats.
    """
    # Mock que lança exceção
    class BrokenPredictor:
        def get_model_info(self):
            raise ValueError("Modelo corrompido")

    with app.app_context():
        app.extensions['predictor'] = BrokenPredictor()

        response = client.get('/api/ml/stats')
        assert response.status_code == 500

        data = response.get_json()
        assert 'error' in data
        assert 'details' in data
