"""
API endpoints para autenticação.
"""
from flask import Blueprint, request, jsonify, current_app
from functools import wraps

from app.services import AuthService


auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


def get_auth_service() -> AuthService:
    """Obtém instância do AuthService."""
    return current_app.extensions['auth_service']


def token_required(f):
    """
    Decorator para proteger rotas que requerem autenticação.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')

        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]

        if not token:
            return jsonify({'error': 'Token não fornecido'}), 401

        auth_service = get_auth_service()
        success, user, error = auth_service.get_user_from_token(token)

        if not success:
            return jsonify({'error': error}), 401

        # Passar usuário para a função decorada
        return f(current_user=user, *args, **kwargs)

    return decorated


def admin_required(f):
    """
    Decorator para proteger rotas que requerem privilégios de admin.
    """
    @wraps(f)
    @token_required
    def decorated(current_user, *args, **kwargs):
        if not current_user.is_admin:
            return jsonify({'error': 'Acesso negado. Privilégios de administrador requeridos'}), 403

        return f(current_user=current_user, *args, **kwargs)

    return decorated


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Registra um novo usuário.

    Request JSON:
        {
            "email": "user@example.com",
            "password": "senha123",
            "full_name": "João Silva"
        }

    Response JSON:
        {
            "user": {...},
            "message": "Usuário criado com sucesso"
        }
    """
    data = request.get_json()

    if not data:
        return jsonify({'error': 'Dados não fornecidos'}), 400

    email = data.get('email')
    password = data.get('password')
    full_name = data.get('full_name')

    if not all([email, password, full_name]):
        return jsonify({'error': 'Email, senha e nome completo são obrigatórios'}), 400

    auth_service = get_auth_service()
    success, user, error = auth_service.register_user(email, password, full_name)

    if not success:
        return jsonify({'error': error}), 400

    # Gerar tokens para auto-login após cadastro
    access_token = auth_service.generate_access_token(user)
    refresh_token = auth_service.generate_refresh_token(user)

    return jsonify({
        'user': user.to_dict(),
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'Bearer',
        'expires_in': auth_service.access_token_expires,
        'message': 'Usuário criado com sucesso'
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Realiza login do usuário.

    Request JSON:
        {
            "email": "user@example.com",
            "password": "senha123"
        }

    Response JSON:
        {
            "user": {...},
            "access_token": "...",
            "refresh_token": "...",
            "token_type": "Bearer",
            "expires_in": 3600
        }
    """
    data = request.get_json()

    if not data:
        return jsonify({'error': 'Dados não fornecidos'}), 400

    email = data.get('email')
    password = data.get('password')

    if not all([email, password]):
        return jsonify({'error': 'Email e senha são obrigatórios'}), 400

    auth_service = get_auth_service()
    success, login_data, error = auth_service.login(email, password)

    if not success:
        return jsonify({'error': error}), 401

    return jsonify(login_data), 200


@auth_bp.route('/refresh', methods=['POST'])
def refresh():
    """
    Renova o access token usando um refresh token.

    Request JSON:
        {
            "refresh_token": "..."
        }

    Response JSON:
        {
            "access_token": "...",
            "token_type": "Bearer",
            "expires_in": 3600
        }
    """
    data = request.get_json()

    if not data:
        return jsonify({'error': 'Dados não fornecidos'}), 400

    refresh_token = data.get('refresh_token')

    if not refresh_token:
        return jsonify({'error': 'Refresh token não fornecido'}), 400

    auth_service = get_auth_service()
    success, new_access_token, error = auth_service.refresh_access_token(refresh_token)

    if not success:
        return jsonify({'error': error}), 401

    return jsonify({
        'access_token': new_access_token,
        'token_type': 'Bearer',
        'expires_in': auth_service.access_token_expires
    }), 200


@auth_bp.route('/me', methods=['GET'])
@token_required
def get_current_user(current_user):
    """
    Retorna informações do usuário autenticado.

    Response JSON:
        {
            "user": {...}
        }
    """
    return jsonify({'user': current_user.to_dict()}), 200


@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout(current_user):
    """
    Logout do usuário (no JWT, apenas informativo - cliente deve descartar tokens).

    Response JSON:
        {
            "message": "Logout realizado com sucesso"
        }
    """
    return jsonify({'message': 'Logout realizado com sucesso'}), 200


@auth_bp.route('/change-password', methods=['PUT'])
@token_required
def change_password(current_user):
    """
    Altera a senha do usuário autenticado.

    Request JSON:
        {
            "current_password": "senha_atual",
            "new_password": "nova_senha",
            "confirm_password": "nova_senha"
        }

    Response JSON:
        {
            "message": "Senha alterada com sucesso"
        }
    """
    data = request.get_json()

    if not data:
        return jsonify({'error': 'Dados não fornecidos'}), 400

    current_password = data.get('current_password')
    new_password = data.get('new_password')
    confirm_password = data.get('confirm_password')

    if not all([current_password, new_password, confirm_password]):
        return jsonify({'error': 'Senha atual, nova senha e confirmação são obrigatórios'}), 400

    if new_password != confirm_password:
        return jsonify({'error': 'Nova senha e confirmação não conferem'}), 400

    auth_service = get_auth_service()
    success, error = auth_service.change_password(
        user_id=current_user.id,
        current_password=current_password,
        new_password=new_password
    )

    if not success:
        return jsonify({'error': error}), 400

    return jsonify({'message': 'Senha alterada com sucesso'}), 200
