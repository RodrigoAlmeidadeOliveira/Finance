"""
Transaction model for manual financial transactions.
Separate from PendingTransaction (import-based) - these are user-created entries.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SQLEnum, Boolean, Text
from sqlalchemy.orm import relationship
import enum

from app.database import Base


class TransactionType(enum.Enum):
    """Transaction type enumeration"""
    INCOME = "income"
    EXPENSE = "expense"


class TransactionStatus(enum.Enum):
    """Transaction status enumeration"""
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Transaction(Base):
    """
    Manual transactions created by users.

    Represents actual financial movements (income/expense) that users
    track in their cash flow. These are independent of imported OFX data.
    """
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    # Dates
    event_date = Column(DateTime, nullable=False, index=True)
    """Date when the transaction actually occurred"""

    effective_date = Column(DateTime, nullable=True)
    """Date when transaction affects account balance (defaults to event_date)"""

    # Classification
    transaction_type = Column(SQLEnum(TransactionType), nullable=False, index=True)
    """INCOME or EXPENSE"""

    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False, index=True)
    """Main category (required)"""

    # Financial details
    institution_id = Column(Integer, ForeignKey('institutions.id'), nullable=True)
    """Bank/account where transaction occurred"""

    credit_card_id = Column(Integer, ForeignKey('credit_cards.id'), nullable=True)
    """Credit card used (optional)"""

    amount = Column(Float, nullable=False)
    """Transaction amount (always positive, type determines direction)"""

    # Description
    description = Column(String(500), nullable=False)
    """User-friendly description of the transaction"""

    notes = Column(Text, nullable=True)
    """Additional notes/observations"""

    # Status
    status = Column(SQLEnum(TransactionStatus), nullable=False, default=TransactionStatus.PENDING, index=True)
    """PENDING (future/unpaid) or COMPLETED (processed)"""

    # Recurrence
    is_recurring = Column(Boolean, default=False)
    """Flag indicating if this is part of a recurring series"""

    recurrence_parent_id = Column(Integer, ForeignKey('transactions.id'), nullable=True)
    """If this was auto-generated from a recurring transaction, link to parent"""

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Soft delete
    deleted_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship('User', backref='transactions')
    category = relationship('Category', backref='transactions')
    institution = relationship('Institution', backref='transactions')
    credit_card = relationship('CreditCard', backref='transactions')

    # Recurring transactions (self-referential)
    recurrence_parent = relationship(
        'Transaction',
        remote_side=[id],
        backref='recurrence_children'
    )

    def __repr__(self):
        return f"<Transaction {self.id}: {self.transaction_type.value} {self.amount} - {self.description[:30]}>"

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'event_date': self.event_date.isoformat() if self.event_date else None,
            'effective_date': self.effective_date.isoformat() if self.effective_date else None,
            'transaction_type': self.transaction_type.value,
            'category_id': self.category_id,
            'category': self.category.to_dict() if self.category else None,
            'institution_id': self.institution_id,
            'institution': self.institution.to_dict() if self.institution else None,
            'credit_card_id': self.credit_card_id,
            'credit_card': {
                'id': self.credit_card.id,
                'name': self.credit_card.name,
                'last_four_digits': self.credit_card.last_four_digits
            } if self.credit_card else None,
            'amount': self.amount,
            'description': self.description,
            'notes': self.notes,
            'status': self.status.value,
            'is_recurring': self.is_recurring,
            'recurrence_parent_id': self.recurrence_parent_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'deleted_at': self.deleted_at.isoformat() if self.deleted_at else None
        }

    @property
    def is_income(self):
        """Check if transaction is income"""
        return self.transaction_type == TransactionType.INCOME

    @property
    def is_expense(self):
        """Check if transaction is expense"""
        return self.transaction_type == TransactionType.EXPENSE

    @property
    def signed_amount(self):
        """
        Return amount with sign based on type.
        Income = positive, Expense = negative
        """
        return self.amount if self.is_income else -self.amount

    @property
    def is_completed(self):
        """Check if transaction is completed"""
        return self.status == TransactionStatus.COMPLETED

    @property
    def is_pending(self):
        """Check if transaction is pending"""
        return self.status == TransactionStatus.PENDING
