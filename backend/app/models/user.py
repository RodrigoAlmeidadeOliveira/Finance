"""
Modelo de usuário para autenticação.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
import bcrypt

from .base import Base


class User(Base):
    """
    Modelo de usuário do sistema.

    Attributes:
        id: ID único do usuário
        email: Email do usuário (único)
        password_hash: Hash da senha (bcrypt)
        full_name: Nome completo do usuário
        is_active: Flag indicando se usuário está ativo
        is_admin: Flag indicando se é administrador
        created_at: Data de criação
        updated_at: Data de atualização
    """

    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relacionamentos
    import_batches = relationship(
        'ImportBatch',
        foreign_keys='ImportBatch.user_id',
        backref='user',
        lazy='dynamic'
    )
    training_jobs = relationship(
        'TrainingJob',
        foreign_keys='TrainingJob.user_id',
        back_populates='user',
        lazy='dynamic'
    )

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', name='{self.full_name}')>"

    def set_password(self, password: str):
        """
        Define a senha do usuário (cria hash bcrypt).

        Args:
            password: Senha em texto plano
        """
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def check_password(self, password: str) -> bool:
        """
        Verifica se a senha fornecida está correta.

        Args:
            password: Senha em texto plano

        Returns:
            True se a senha estiver correta
        """
        return bcrypt.checkpw(
            password.encode('utf-8'),
            self.password_hash.encode('utf-8')
        )

    def to_dict(self, include_sensitive=False):
        """
        Converte usuário para dicionário.

        Args:
            include_sensitive: Se True, inclui dados sensíveis

        Returns:
            Dicionário com dados do usuário
        """
        data = {
            'id': self.id,
            'email': self.email,
            'full_name': self.full_name,
            'is_active': self.is_active,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

        if include_sensitive:
            data['password_hash'] = self.password_hash

        return data

    @classmethod
    def create_user(cls, email: str, password: str, full_name: str, is_admin: bool = False):
        """
        Factory method para criar novo usuário.

        Args:
            email: Email do usuário
            password: Senha em texto plano
            full_name: Nome completo
            is_admin: Se é administrador

        Returns:
            Instância de User
        """
        user = cls(
            email=email.lower().strip(),
            full_name=full_name.strip(),
            is_admin=is_admin
        )
        user.set_password(password)
        return user
