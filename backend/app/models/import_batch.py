"""
Modelo para lotes de importação OFX.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Float, Text, Enum, ForeignKey
from sqlalchemy.orm import relationship
import enum

from .base import Base


class ImportStatus(enum.Enum):
    """Status do lote de importação."""
    PENDING = "pending"  # Upload feito, aguardando processamento
    PROCESSING = "processing"  # Processando arquivo
    REVIEW = "review"  # Aguardando revisão do usuário
    COMPLETED = "completed"  # Confirmado e transações criadas
    FAILED = "failed"  # Erro no processamento
    CANCELLED = "cancelled"  # Cancelado pelo usuário


class ImportBatch(Base):
    """
    Representa um lote de importação de arquivo OFX.

    Attributes:
        id: ID único do lote
        user_id: ID do usuário que fez o upload
        filename: Nome do arquivo original
        file_path: Caminho do arquivo no servidor
        status: Status do processamento
        institution_name: Nome da instituição financeira
        account_id: ID da conta no banco
        total_transactions: Número total de transações
        processed_transactions: Transações processadas
        period_start: Data início do período
        period_end: Data fim do período
        balance: Saldo final da conta
        created_at: Data de criação
        updated_at: Data de atualização
        error_message: Mensagem de erro (se houver)
    """

    __tablename__ = 'import_batches'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=True)
    status = Column(
        Enum(ImportStatus),
        default=ImportStatus.PENDING,
        nullable=False
    )

    # Informações da instituição/conta
    institution_name = Column(String(255), nullable=True)
    account_id = Column(String(100), nullable=True)

    # Estatísticas
    total_transactions = Column(Integer, default=0)
    processed_transactions = Column(Integer, default=0)

    # Período
    period_start = Column(DateTime, nullable=True)
    period_end = Column(DateTime, nullable=True)

    # Saldo
    balance = Column(Float, nullable=True)

    # Metadados
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    error_message = Column(Text, nullable=True)

    # Relacionamentos
    pending_transactions = relationship(
        'PendingTransaction',
        back_populates='import_batch',
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f"<ImportBatch(id={self.id}, filename='{self.filename}', status={self.status.value})>"

    def to_dict(self):
        """Converte para dicionário."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'filename': self.filename,
            'status': self.status.value,
            'institution_name': self.institution_name,
            'account_id': self.account_id,
            'total_transactions': self.total_transactions,
            'processed_transactions': self.processed_transactions,
            'period_start': self.period_start.isoformat() if self.period_start else None,
            'period_end': self.period_end.isoformat() if self.period_end else None,
            'balance': self.balance,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'error_message': self.error_message
        }
