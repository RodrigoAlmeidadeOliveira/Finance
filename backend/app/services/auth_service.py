"""
Serviço de autenticação e gerenciamento de usuários.
"""
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
import jwt

from app.models import User
from app.database import get_session


class AuthService:
    """
    Serviço para autenticação de usuários e geração de tokens JWT.
    """

    def __init__(self, jwt_secret: str, jwt_algorithm: str = 'HS256',
                 access_token_expires: int = 3600, refresh_token_expires: int = 2592000):
        """
        Inicializa o serviço de autenticação.

        Args:
            jwt_secret: Chave secreta para assinar tokens JWT
            jwt_algorithm: Algoritmo de assinatura JWT
            access_token_expires: Tempo de expiração do access token em segundos (padrão: 1 hora)
            refresh_token_expires: Tempo de expiração do refresh token em segundos (padrão: 30 dias)
        """
        self.jwt_secret = jwt_secret
        self.jwt_algorithm = jwt_algorithm
        self.access_token_expires = access_token_expires
        self.refresh_token_expires = refresh_token_expires

    def register_user(self, email: str, password: str, full_name: str,
                     is_admin: bool = False) -> Tuple[bool, Optional[User], Optional[str]]:
        """
        Registra um novo usuário no sistema.

        Args:
            email: Email do usuário
            password: Senha em texto plano
            full_name: Nome completo
            is_admin: Se é administrador

        Returns:
            Tupla (sucesso, usuário, mensagem_erro)
        """
        session = get_session()

        try:
            # Verificar se email já existe
            existing_user = session.query(User).filter(User.email == email.lower()).first()

            if existing_user:
                return False, None, "Email já cadastrado"

            # Validar dados
            if not email or not password or not full_name:
                return False, None, "Todos os campos são obrigatórios"

            if len(password) < 6:
                return False, None, "Senha deve ter no mínimo 6 caracteres"

            # Criar usuário
            user = User.create_user(
                email=email,
                password=password,
                full_name=full_name,
                is_admin=is_admin
            )

            session.add(user)
            session.commit()
            session.refresh(user)

            return True, user, None

        except Exception as e:
            session.rollback()
            return False, None, f"Erro ao criar usuário: {str(e)}"

    def authenticate_user(self, email: str, password: str) -> Tuple[bool, Optional[User], Optional[str]]:
        """
        Autentica um usuário.

        Args:
            email: Email do usuário
            password: Senha em texto plano

        Returns:
            Tupla (sucesso, usuário, mensagem_erro)
        """
        session = get_session()

        try:
            # Buscar usuário
            user = session.query(User).filter(User.email == email.lower()).first()

            if not user:
                return False, None, "Credenciais inválidas"

            if not user.is_active:
                return False, None, "Usuário desativado"

            # Verificar senha
            if not user.check_password(password):
                return False, None, "Credenciais inválidas"

            return True, user, None

        except Exception as e:
            return False, None, f"Erro ao autenticar: {str(e)}"

    def generate_access_token(self, user: User) -> str:
        """
        Gera um access token JWT para o usuário.

        Args:
            user: Instância do usuário

        Returns:
            Token JWT codificado
        """
        payload = {
            'user_id': user.id,
            'email': user.email,
            'is_admin': user.is_admin,
            'exp': datetime.utcnow() + timedelta(seconds=self.access_token_expires),
            'iat': datetime.utcnow(),
            'type': 'access'
        }

        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)

    def generate_refresh_token(self, user: User) -> str:
        """
        Gera um refresh token JWT para o usuário.

        Args:
            user: Instância do usuário

        Returns:
            Token JWT codificado
        """
        payload = {
            'user_id': user.id,
            'exp': datetime.utcnow() + timedelta(seconds=self.refresh_token_expires),
            'iat': datetime.utcnow(),
            'type': 'refresh'
        }

        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)

    def verify_token(self, token: str, token_type: str = 'access') -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        Verifica e decodifica um token JWT.

        Args:
            token: Token JWT codificado
            token_type: Tipo do token ('access' ou 'refresh')

        Returns:
            Tupla (válido, payload, mensagem_erro)
        """
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])

            # Verificar tipo do token
            if payload.get('type') != token_type:
                return False, None, "Tipo de token inválido"

            return True, payload, None

        except jwt.ExpiredSignatureError:
            return False, None, "Token expirado"
        except jwt.InvalidTokenError as e:
            return False, None, f"Token inválido: {str(e)}"

    def get_user_from_token(self, token: str) -> Tuple[bool, Optional[User], Optional[str]]:
        """
        Obtém o usuário a partir de um token JWT.

        Args:
            token: Token JWT codificado

        Returns:
            Tupla (sucesso, usuário, mensagem_erro)
        """
        # Verificar token
        valid, payload, error = self.verify_token(token, token_type='access')

        if not valid:
            return False, None, error

        session = get_session()

        try:
            # Buscar usuário
            user = session.query(User).filter(User.id == payload['user_id']).first()

            if not user:
                return False, None, "Usuário não encontrado"

            if not user.is_active:
                return False, None, "Usuário desativado"

            return True, user, None

        except Exception as e:
            return False, None, f"Erro ao buscar usuário: {str(e)}"

    def refresh_access_token(self, refresh_token: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Gera um novo access token a partir de um refresh token válido.

        Args:
            refresh_token: Refresh token JWT

        Returns:
            Tupla (sucesso, novo_access_token, mensagem_erro)
        """
        # Verificar refresh token
        valid, payload, error = self.verify_token(refresh_token, token_type='refresh')

        if not valid:
            return False, None, error

        session = get_session()

        try:
            # Buscar usuário
            user = session.query(User).filter(User.id == payload['user_id']).first()

            if not user or not user.is_active:
                return False, None, "Usuário inválido ou desativado"

            # Gerar novo access token
            new_access_token = self.generate_access_token(user)

            return True, new_access_token, None

        except Exception as e:
            return False, None, f"Erro ao renovar token: {str(e)}"

    def change_password(self, user_id: int, current_password: str,
                        new_password: str) -> Tuple[bool, Optional[str]]:
        """
        Altera a senha de um usuário autenticado.

        Args:
            user_id: ID do usuário
            current_password: Senha atual
            new_password: Nova senha

        Returns:
            Tupla (sucesso, mensagem_erro)
        """
        session = get_session()

        try:
            user = session.query(User).filter(User.id == user_id).first()

            if not user:
                return False, "Usuário não encontrado"

            if not user.is_active:
                return False, "Usuário desativado"

            # Verificar senha atual
            if not user.check_password(current_password):
                return False, "Senha atual incorreta"

            # Validar nova senha
            if len(new_password) < 6:
                return False, "Nova senha deve ter no mínimo 6 caracteres"

            # Atualizar senha
            user.set_password(new_password)
            session.commit()

            return True, None

        except Exception as e:
            session.rollback()
            return False, f"Erro ao alterar senha: {str(e)}"

    def login(self, email: str, password: str) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        Realiza login completo (autentica e gera tokens).

        Args:
            email: Email do usuário
            password: Senha

        Returns:
            Tupla (sucesso, dados_login, mensagem_erro)
            dados_login contém: user, access_token, refresh_token
        """
        # Autenticar
        success, user, error = self.authenticate_user(email, password)

        if not success:
            return False, None, error

        # Gerar tokens
        access_token = self.generate_access_token(user)
        refresh_token = self.generate_refresh_token(user)

        login_data = {
            'user': user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'Bearer',
            'expires_in': self.access_token_expires
        }

        return True, login_data, None
