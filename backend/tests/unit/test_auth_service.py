"""
Testes unitários para o AuthService.
"""
import pytest

from app import create_app
from app.database import get_engine, get_session, remove_session
from app.models import Base, User
from app.services import AuthService


@pytest.fixture(scope="function")
def app():
    app = create_app("testing")
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    yield app
    Base.metadata.drop_all(bind=engine)
    remove_session()


@pytest.fixture()
def auth_service(app):
    with app.app_context():
        return app.extensions['auth_service']


@pytest.fixture()
def sample_user(app):
    """Cria um usuário de teste no banco."""
    with app.app_context():
        session = get_session()
        user = User.create_user(
            email='teste@example.com',
            password='senha123',
            full_name='Usuário Teste'
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user


class TestRegisterUser:
    def test_register_user_success(self, app, auth_service):
        with app.app_context():
            success, user, error = auth_service.register_user(
                email='novo@example.com',
                password='senha123',
                full_name='Novo Usuário'
            )
            assert success is True
            assert user is not None
            assert user.email == 'novo@example.com'
            assert user.full_name == 'Novo Usuário'
            assert error is None

    def test_register_user_duplicate_email(self, app, auth_service, sample_user):
        with app.app_context():
            success, user, error = auth_service.register_user(
                email='teste@example.com',
                password='outra_senha',
                full_name='Outro Nome'
            )
            assert success is False
            assert user is None
            assert 'já cadastrado' in error

    def test_register_user_short_password(self, app, auth_service):
        with app.app_context():
            success, user, error = auth_service.register_user(
                email='curta@example.com',
                password='123',
                full_name='Senha Curta'
            )
            assert success is False
            assert 'mínimo 6' in error

    def test_register_user_missing_fields(self, app, auth_service):
        with app.app_context():
            success, user, error = auth_service.register_user(
                email='',
                password='senha123',
                full_name='Sem Email'
            )
            assert success is False

    def test_register_user_password_is_hashed(self, app, auth_service):
        with app.app_context():
            success, user, error = auth_service.register_user(
                email='hash@example.com',
                password='minha_senha',
                full_name='Hash Test'
            )
            assert success is True
            assert user.password_hash != 'minha_senha'
            assert user.check_password('minha_senha')


class TestAuthenticateUser:
    def test_authenticate_success(self, app, auth_service, sample_user):
        with app.app_context():
            success, user, error = auth_service.authenticate_user(
                'teste@example.com', 'senha123'
            )
            assert success is True
            assert user is not None
            assert user.email == 'teste@example.com'

    def test_authenticate_wrong_password(self, app, auth_service, sample_user):
        with app.app_context():
            success, user, error = auth_service.authenticate_user(
                'teste@example.com', 'errada'
            )
            assert success is False
            assert 'Credenciais inválidas' in error

    def test_authenticate_nonexistent_user(self, app, auth_service):
        with app.app_context():
            success, user, error = auth_service.authenticate_user(
                'naoexiste@example.com', 'qualquer'
            )
            assert success is False
            assert 'Credenciais inválidas' in error


class TestChangePassword:
    def test_change_password_success(self, app, auth_service, sample_user):
        with app.app_context():
            success, error = auth_service.change_password(
                user_id=sample_user.id,
                current_password='senha123',
                new_password='nova_senha456'
            )
            assert success is True
            assert error is None

            # Verificar que a nova senha funciona
            auth_success, user, _ = auth_service.authenticate_user(
                'teste@example.com', 'nova_senha456'
            )
            assert auth_success is True

    def test_change_password_wrong_current(self, app, auth_service, sample_user):
        with app.app_context():
            success, error = auth_service.change_password(
                user_id=sample_user.id,
                current_password='errada',
                new_password='nova_senha456'
            )
            assert success is False
            assert 'incorreta' in error

    def test_change_password_short_new_password(self, app, auth_service, sample_user):
        with app.app_context():
            success, error = auth_service.change_password(
                user_id=sample_user.id,
                current_password='senha123',
                new_password='12'
            )
            assert success is False
            assert 'mínimo 6' in error

    def test_change_password_nonexistent_user(self, app, auth_service):
        with app.app_context():
            success, error = auth_service.change_password(
                user_id=99999,
                current_password='qualquer',
                new_password='nova_senha456'
            )
            assert success is False
            assert 'não encontrado' in error

    def test_change_password_old_password_stops_working(self, app, auth_service, sample_user):
        with app.app_context():
            auth_service.change_password(
                user_id=sample_user.id,
                current_password='senha123',
                new_password='nova_senha456'
            )

            # Senha antiga não deve funcionar mais
            auth_success, _, _ = auth_service.authenticate_user(
                'teste@example.com', 'senha123'
            )
            assert auth_success is False


class TestTokens:
    def test_login_returns_tokens(self, app, auth_service, sample_user):
        with app.app_context():
            success, login_data, error = auth_service.login(
                'teste@example.com', 'senha123'
            )
            assert success is True
            assert 'access_token' in login_data
            assert 'refresh_token' in login_data
            assert login_data['token_type'] == 'Bearer'

    def test_verify_access_token(self, app, auth_service, sample_user):
        with app.app_context():
            _, login_data, _ = auth_service.login('teste@example.com', 'senha123')
            valid, payload, error = auth_service.verify_token(
                login_data['access_token'], token_type='access'
            )
            assert valid is True
            assert payload['user_id'] == sample_user.id

    def test_refresh_token_generates_new_access(self, app, auth_service, sample_user):
        with app.app_context():
            _, login_data, _ = auth_service.login('teste@example.com', 'senha123')
            success, new_token, error = auth_service.refresh_access_token(
                login_data['refresh_token']
            )
            assert success is True
            assert new_token is not None
