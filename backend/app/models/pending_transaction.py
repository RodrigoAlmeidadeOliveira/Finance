"""
Modelo para transações pendentes de classificação.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Float, Text, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum

from .base import Base


class ReviewStatus(enum.Enum):
    """Status de revisão da transação."""
    PENDING = "pending"  # Aguardando revisão
    APPROVED = "approved"  # Aprovada pelo usuário
    MODIFIED = "modified"  # Modificada pelo usuário
    REJECTED = "rejected"  # Rejeitada


class PendingTransaction(Base):
    """
    Transação pendente de classificação/revisão após importação OFX.

    Attributes:
        id: ID único da transação pendente
        import_batch_id: ID do lote de importação
        fitid: ID da transação do OFX (para detectar duplicatas)
        date: Data da transação
        description: Descrição/memo da transação
        amount: Valor (positivo=crédito, negativo=débito)
        transaction_type: Tipo (débito/crédito)
        predicted_category: Categoria prevista pelo ML
        confidence_score: Score de confiança da predição (0-1)
        confidence_level: Nível de confiança (high/medium/low)
        suggested_categories: JSON com sugestões alternativas
        user_category: Categoria escolhida pelo usuário (se modificada)
        review_status: Status de revisão
        reviewed_at: Data de revisão
        notes: Notas do usuário
        created_at: Data de criação
    """

    __tablename__ = 'pending_transactions'

    id = Column(Integer, primary_key=True)
    import_batch_id = Column(Integer, ForeignKey('import_batches.id'), nullable=False)

    # Dados da transação OFX
    fitid = Column(String(255), nullable=False)  # Financial Transaction ID
    date = Column(DateTime, nullable=False)
    description = Column(Text, nullable=False)
    amount = Column(Float, nullable=False)
    transaction_type = Column(String(20), nullable=False)  # 'debito' ou 'credito'

    # Dados adicionais do OFX
    payee = Column(String(255), nullable=True)
    memo = Column(Text, nullable=True)
    check_number = Column(String(50), nullable=True)
    ofx_type = Column(String(50), nullable=True)

    # Predição ML
    predicted_category = Column(String(100), nullable=True)
    confidence_score = Column(Float, nullable=True)  # 0.0 a 1.0
    confidence_level = Column(String(20), nullable=True)  # 'high', 'medium', 'low'
    suggested_categories = Column(Text, nullable=True)  # JSON com alternativas

    # Revisão do usuário
    user_category = Column(String(100), nullable=True)
    review_status = Column(
        Enum(ReviewStatus),
        default=ReviewStatus.PENDING,
        nullable=False
    )
    reviewed_at = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)

    # Metadados
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relacionamentos
    import_batch = relationship('ImportBatch', back_populates='pending_transactions')

    def __repr__(self):
        return f"<PendingTransaction(id={self.id}, fitid='{self.fitid}', date={self.date})>"

    def to_dict(self):
        """Converte para dicionário."""
        import json

        # Parse suggested_categories se for JSON string
        suggestions = None
        if self.suggested_categories:
            try:
                suggestions = json.loads(self.suggested_categories)
            except:
                suggestions = None

        return {
            'id': self.id,
            'import_batch_id': self.import_batch_id,
            'fitid': self.fitid,
            'date': self.date.isoformat(),
            'description': self.description,
            'amount': self.amount,
            'transaction_type': self.transaction_type,
            'payee': self.payee,
            'memo': self.memo,
            'check_number': self.check_number,
            'predicted_category': self.predicted_category,
            'confidence_score': self.confidence_score,
            'confidence_level': self.confidence_level,
            'suggested_categories': suggestions,
            'user_category': self.user_category,
            'review_status': self.review_status.value,
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None,
            'notes': self.notes,
            'created_at': self.created_at.isoformat()
        }

    @property
    def final_category(self):
        """Retorna a categoria final (usuário tem precedência)."""
        return self.user_category or self.predicted_category

    @property
    def needs_review(self):
        """Verifica se precisa de revisão."""
        return (
            self.review_status == ReviewStatus.PENDING and
            (self.confidence_level == 'low' or self.confidence_score < 0.6)
        )
