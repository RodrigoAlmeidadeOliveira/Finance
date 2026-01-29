"""
Testes de integração para os endpoints de autenticação.
"""
import pytest

from app import create_app
from app.database import get_engine, get_session, remove_session
from app.models import Base, User


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


@pytest.fixture()
def registered_user(app, client):
    """Registra um usuário e retorna os dados de registro."""
    resp = client.post('/api/auth/register', json={
        'email': 'teste@example.com',
        'password': 'senha123',
        'full_name': 'Usuário Teste'
    })
    return resp.get_json()


@pytest.fixture()
def auth_headers(registered_user):
    """Retorna headers de autenticação com token válido."""
    return {'Authorization': f'Bearer {registered_user["access_token"]}'}


class TestRegisterEndpoint:
    def test_register_success(self, client):
        resp = client.post('/api/auth/register', json={
            'email': 'novo@example.com',
            'password': 'senha123',
            'full_name': 'Novo Usuário'
        })
        assert resp.status_code == 201
        data = resp.get_json()
        assert data['user']['email'] == 'novo@example.com'
        assert data['user']['full_name'] == 'Novo Usuário'
        assert 'access_token' in data
        assert 'refresh_token' in data
        assert data['token_type'] == 'Bearer'
        assert 'password_hash' not in data['user']

    def test_register_duplicate_email(self, client, registered_user):
        resp = client.post('/api/auth/register', json={
            'email': 'teste@example.com',
            'password': 'outra123',
            'full_name': 'Outro Nome'
        })
        assert resp.status_code == 400
        assert 'já cadastrado' in resp.get_json()['error']

    def test_register_missing_fields(self, client):
        resp = client.post('/api/auth/register', json={
            'email': 'incompleto@example.com'
        })
        assert resp.status_code == 400

    def test_register_short_password(self, client):
        resp = client.post('/api/auth/register', json={
            'email': 'curta@example.com',
            'password': '123',
            'full_name': 'Senha Curta'
        })
        assert resp.status_code == 400

    def test_register_no_body(self, client):
        resp = client.post('/api/auth/register',
                           content_type='application/json')
        assert resp.status_code == 400


class TestLoginEndpoint:
    def test_login_success(self, client, registered_user):
        resp = client.post('/api/auth/login', json={
            'email': 'teste@example.com',
            'password': 'senha123'
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'access_token' in data
        assert 'refresh_token' in data
        assert data['user']['email'] == 'teste@example.com'

    def test_login_wrong_password(self, client, registered_user):
        resp = client.post('/api/auth/login', json={
            'email': 'teste@example.com',
            'password': 'errada'
        })
        assert resp.status_code == 401
        assert 'error' in resp.get_json()

    def test_login_nonexistent_user(self, client):
        resp = client.post('/api/auth/login', json={
            'email': 'naoexiste@example.com',
            'password': 'qualquer'
        })
        assert resp.status_code == 401

    def test_login_missing_fields(self, client):
        resp = client.post('/api/auth/login', json={
            'email': 'teste@example.com'
        })
        assert resp.status_code == 400


class TestChangePasswordEndpoint:
    def test_change_password_success(self, client, auth_headers):
        resp = client.put('/api/auth/change-password',
                          json={
                              'current_password': 'senha123',
                              'new_password': 'nova_senha456',
                              'confirm_password': 'nova_senha456'
                          },
                          headers=auth_headers)
        assert resp.status_code == 200
        assert 'Senha alterada' in resp.get_json()['message']

        # Verificar login com nova senha
        login_resp = client.post('/api/auth/login', json={
            'email': 'teste@example.com',
            'password': 'nova_senha456'
        })
        assert login_resp.status_code == 200

    def test_change_password_wrong_current(self, client, auth_headers):
        resp = client.put('/api/auth/change-password',
                          json={
                              'current_password': 'errada',
                              'new_password': 'nova_senha456',
                              'confirm_password': 'nova_senha456'
                          },
                          headers=auth_headers)
        assert resp.status_code == 400
        assert 'incorreta' in resp.get_json()['error']

    def test_change_password_mismatch_confirm(self, client, auth_headers):
        resp = client.put('/api/auth/change-password',
                          json={
                              'current_password': 'senha123',
                              'new_password': 'nova_senha456',
                              'confirm_password': 'diferente789'
                          },
                          headers=auth_headers)
        assert resp.status_code == 400
        assert 'não conferem' in resp.get_json()['error']

    def test_change_password_short_new(self, client, auth_headers):
        resp = client.put('/api/auth/change-password',
                          json={
                              'current_password': 'senha123',
                              'new_password': '12',
                              'confirm_password': '12'
                          },
                          headers=auth_headers)
        assert resp.status_code == 400

    def test_change_password_missing_fields(self, client, auth_headers):
        resp = client.put('/api/auth/change-password',
                          json={
                              'current_password': 'senha123'
                          },
                          headers=auth_headers)
        assert resp.status_code == 400

    def test_change_password_no_auth(self, client):
        resp = client.put('/api/auth/change-password',
                          json={
                              'current_password': 'senha123',
                              'new_password': 'nova_senha456',
                              'confirm_password': 'nova_senha456'
                          })
        assert resp.status_code == 401

    def test_change_password_old_password_invalid(self, client, auth_headers):
        # Alterar senha
        client.put('/api/auth/change-password',
                   json={
                       'current_password': 'senha123',
                       'new_password': 'nova_senha456',
                       'confirm_password': 'nova_senha456'
                   },
                   headers=auth_headers)

        # Tentar login com senha antiga
        login_resp = client.post('/api/auth/login', json={
            'email': 'teste@example.com',
            'password': 'senha123'
        })
        assert login_resp.status_code == 401


class TestMeEndpoint:
    def test_me_success(self, client, auth_headers):
        resp = client.get('/api/auth/me', headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['user']['email'] == 'teste@example.com'

    def test_me_no_auth(self, client):
        resp = client.get('/api/auth/me')
        assert resp.status_code == 401


class TestRefreshEndpoint:
    def test_refresh_success(self, client, registered_user):
        resp = client.post('/api/auth/refresh', json={
            'refresh_token': registered_user['refresh_token']
        })
        assert resp.status_code == 200
        assert 'access_token' in resp.get_json()

    def test_refresh_invalid_token(self, client):
        resp = client.post('/api/auth/refresh', json={
            'refresh_token': 'token_invalido'
        })
        assert resp.status_code == 401
