"""
Service for manual transaction management (cash flow).
"""
from __future__ import annotations

from contextlib import contextmanager
from datetime import date, datetime, timedelta
from typing import Callable, Dict, List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, extract

from ..models import (
    Category,
    CreditCard,
    Institution,
    Transaction,
    TransactionType,
    TransactionStatus,
)


def _parse_date(value: Optional[str]) -> Optional[datetime]:
    """Parse ISO format string to datetime"""
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError:
        return None


class TransactionService:
    """CRUD and business logic for manual transactions"""

    def __init__(self, session_factory: Callable[[], Session]):
        self.session_factory = session_factory

    @contextmanager
    def _session_scope(self):
        """Context manager for database sessions"""
        session = self.session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    # --- CRUD Operations ---

    def create_transaction(
        self,
        *,
        user_id: int,
        event_date: str,
        transaction_type: str,
        category_id: int,
        amount: float,
        description: str,
        effective_date: Optional[str] = None,
        institution_id: Optional[int] = None,
        credit_card_id: Optional[int] = None,
        notes: Optional[str] = None,
        status: str = "PENDING",
        is_recurring: bool = False,
    ) -> dict:
        """Create a new manual transaction"""

        # Validations
        if amount <= 0:
            raise ValueError("Amount must be greater than zero")

        if not description or not description.strip():
            raise ValueError("Description is required")

        try:
            trans_type = TransactionType[transaction_type.upper()]
        except KeyError:
            raise ValueError(f"Invalid transaction type: {transaction_type}")

        try:
            trans_status = TransactionStatus[status.upper()]
        except KeyError:
            raise ValueError(f"Invalid status: {status}")

        event_dt = _parse_date(event_date)
        if not event_dt:
            raise ValueError("Invalid event_date format")

        effective_dt = _parse_date(effective_date) if effective_date else event_dt

        with self._session_scope() as session:
            # Validate category exists
            category = session.get(Category, category_id)
            if not category:
                raise ValueError(f"Category {category_id} not found")

            # Validate institution if provided
            if institution_id:
                institution = session.get(Institution, institution_id)
                if not institution:
                    raise ValueError(f"Institution {institution_id} not found")

            # Validate credit card if provided
            if credit_card_id:
                card = session.get(CreditCard, credit_card_id)
                if not card:
                    raise ValueError(f"Credit card {credit_card_id} not found")

            transaction = Transaction(
                user_id=user_id,
                event_date=event_dt,
                effective_date=effective_dt,
                transaction_type=trans_type,
                category_id=category_id,
                amount=amount,
                description=description.strip(),
                notes=notes.strip() if notes else None,
                institution_id=institution_id,
                credit_card_id=credit_card_id,
                status=trans_status,
                is_recurring=is_recurring,
            )

            session.add(transaction)
            session.flush()
            return transaction.to_dict()

    def get_transaction(self, transaction_id: int, user_id: int) -> Optional[dict]:
        """Get transaction by ID (with user validation)"""
        session = self.session_factory()
        try:
            transaction = session.query(Transaction).filter(
                Transaction.id == transaction_id,
                Transaction.user_id == user_id,
                Transaction.deleted_at.is_(None)
            ).first()

            return transaction.to_dict() if transaction else None
        finally:
            session.close()

    def list_transactions(
        self,
        user_id: int,
        *,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        transaction_type: Optional[str] = None,
        category_id: Optional[int] = None,
        institution_id: Optional[int] = None,
        credit_card_id: Optional[int] = None,
        status: Optional[str] = None,
        min_amount: Optional[float] = None,
        max_amount: Optional[float] = None,
        search: Optional[str] = None,
        include_deleted: bool = False,
        limit: int = 100,
        offset: int = 0,
    ) -> Dict[str, any]:
        """
        List transactions with advanced filters.
        Returns dict with 'items' (list of transactions) and 'total' (count)
        """
        session = self.session_factory()
        try:
            query = session.query(Transaction).filter(Transaction.user_id == user_id)

            # Apply filters
            if not include_deleted:
                query = query.filter(Transaction.deleted_at.is_(None))

            if start_date:
                start_dt = _parse_date(start_date)
                if start_dt:
                    query = query.filter(Transaction.event_date >= start_dt)

            if end_date:
                end_dt = _parse_date(end_date)
                if end_dt:
                    query = query.filter(Transaction.event_date <= end_dt)

            if transaction_type:
                try:
                    trans_type = TransactionType[transaction_type.upper()]
                    query = query.filter(Transaction.transaction_type == trans_type)
                except KeyError:
                    pass

            if category_id:
                query = query.filter(Transaction.category_id == category_id)

            if institution_id:
                query = query.filter(Transaction.institution_id == institution_id)

            if credit_card_id:
                query = query.filter(Transaction.credit_card_id == credit_card_id)

            if status:
                try:
                    trans_status = TransactionStatus[status.upper()]
                    query = query.filter(Transaction.status == trans_status)
                except KeyError:
                    pass

            if min_amount is not None:
                query = query.filter(Transaction.amount >= min_amount)

            if max_amount is not None:
                query = query.filter(Transaction.amount <= max_amount)

            if search:
                search_term = f"%{search}%"
                query = query.filter(
                    or_(
                        Transaction.description.ilike(search_term),
                        Transaction.notes.ilike(search_term)
                    )
                )

            # Count total
            total = query.count()

            # Apply pagination and ordering
            transactions = query.order_by(
                Transaction.event_date.desc(),
                Transaction.created_at.desc()
            ).limit(limit).offset(offset).all()

            return {
                'items': [t.to_dict() for t in transactions],
                'total': total,
                'limit': limit,
                'offset': offset
            }
        finally:
            session.close()

    def update_transaction(
        self,
        transaction_id: int,
        user_id: int,
        **updates
    ) -> dict:
        """Update transaction fields"""
        with self._session_scope() as session:
            transaction = session.query(Transaction).filter(
                Transaction.id == transaction_id,
                Transaction.user_id == user_id,
                Transaction.deleted_at.is_(None)
            ).first()

            if not transaction:
                raise ValueError(f"Transaction {transaction_id} not found")

            # Update allowed fields
            allowed_fields = [
                'event_date', 'effective_date', 'transaction_type', 'category_id',
                'amount', 'description', 'notes', 'institution_id', 'credit_card_id',
                'status', 'is_recurring'
            ]

            for field, value in updates.items():
                if field not in allowed_fields:
                    continue

                if field == 'event_date' and value:
                    value = _parse_date(value)
                elif field == 'effective_date' and value:
                    value = _parse_date(value)
                elif field == 'transaction_type' and value:
                    value = TransactionType[value.upper()]
                elif field == 'status' and value:
                    value = TransactionStatus[value.upper()]
                elif field == 'amount' and value:
                    if float(value) <= 0:
                        raise ValueError("Amount must be greater than zero")
                    value = float(value)
                elif field in ['description', 'notes'] and value:
                    value = value.strip()

                setattr(transaction, field, value)

            session.flush()
            return transaction.to_dict()

    def delete_transaction(self, transaction_id: int, user_id: int, soft: bool = True) -> bool:
        """Delete transaction (soft delete by default)"""
        with self._session_scope() as session:
            transaction = session.query(Transaction).filter(
                Transaction.id == transaction_id,
                Transaction.user_id == user_id,
                Transaction.deleted_at.is_(None)
            ).first()

            if not transaction:
                return False

            if soft:
                transaction.deleted_at = datetime.utcnow()
            else:
                session.delete(transaction)

            return True

    # --- Status Management ---

    def mark_as_completed(self, transaction_id: int, user_id: int) -> dict:
        """Mark transaction as completed"""
        return self.update_transaction(
            transaction_id,
            user_id,
            status='COMPLETED'
        )

    def mark_as_pending(self, transaction_id: int, user_id: int) -> dict:
        """Mark transaction as pending"""
        return self.update_transaction(
            transaction_id,
            user_id,
            status='PENDING'
        )

    # --- Bulk Operations ---

    def bulk_update_status(
        self,
        transaction_ids: List[int],
        user_id: int,
        status: str
    ) -> int:
        """Update status for multiple transactions. Returns count updated."""
        try:
            trans_status = TransactionStatus[status.upper()]
        except KeyError:
            raise ValueError(f"Invalid status: {status}")

        with self._session_scope() as session:
            updated = session.query(Transaction).filter(
                Transaction.id.in_(transaction_ids),
                Transaction.user_id == user_id,
                Transaction.deleted_at.is_(None)
            ).update(
                {'status': trans_status},
                synchronize_session=False
            )
            return updated

    # --- Recurrence ---

    def duplicate_transaction(
        self,
        transaction_id: int,
        user_id: int,
        new_event_date: str,
        link_as_recurrence: bool = True
    ) -> dict:
        """Duplicate transaction to a new date (useful for recurring transactions)"""
        session = self.session_factory()
        try:
            original = session.query(Transaction).filter(
                Transaction.id == transaction_id,
                Transaction.user_id == user_id,
                Transaction.deleted_at.is_(None)
            ).first()

            if not original:
                raise ValueError(f"Transaction {transaction_id} not found")

            new_event_dt = _parse_date(new_event_date)
            if not new_event_dt:
                raise ValueError("Invalid new_event_date format")

            # Create duplicate
            new_transaction = Transaction(
                user_id=original.user_id,
                event_date=new_event_dt,
                effective_date=new_event_dt,  # Reset effective date
                transaction_type=original.transaction_type,
                category_id=original.category_id,
                amount=original.amount,
                description=original.description,
                notes=original.notes,
                institution_id=original.institution_id,
                credit_card_id=original.credit_card_id,
                status=TransactionStatus.PENDING,  # Always start as pending
                is_recurring=True,
                recurrence_parent_id=transaction_id if link_as_recurrence else None
            )

            # Mark original as recurring if linking
            if link_as_recurrence:
                original.is_recurring = True

            session.add(new_transaction)
            session.commit()

            return new_transaction.to_dict()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    # --- Analytics ---

    def get_summary(
        self,
        user_id: int,
        start_date: str,
        end_date: str,
        include_pending: bool = False
    ) -> dict:
        """Get financial summary for a period"""
        session = self.session_factory()
        try:
            start_dt = _parse_date(start_date)
            end_dt = _parse_date(end_date)

            query = session.query(Transaction).filter(
                Transaction.user_id == user_id,
                Transaction.deleted_at.is_(None),
                Transaction.event_date >= start_dt,
                Transaction.event_date <= end_dt
            )

            if not include_pending:
                query = query.filter(Transaction.status == TransactionStatus.COMPLETED)

            transactions = query.all()

            income = sum(t.amount for t in transactions if t.is_income)
            expense = sum(t.amount for t in transactions if t.is_expense)
            balance = income - expense

            return {
                'period': {
                    'start': start_date,
                    'end': end_date
                },
                'income': round(income, 2),
                'expense': round(expense, 2),
                'balance': round(balance, 2),
                'transaction_count': len(transactions),
                'income_count': sum(1 for t in transactions if t.is_income),
                'expense_count': sum(1 for t in transactions if t.is_expense)
            }
        finally:
            session.close()

    def get_monthly_summary(
        self,
        user_id: int,
        year: int,
        month: int,
        include_pending: bool = False
    ) -> dict:
        """Get summary for a specific month"""
        # Calculate month boundaries
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(days=1)

        return self.get_summary(
            user_id,
            start_date.isoformat(),
            end_date.isoformat(),
            include_pending
        )

    def get_by_category(
        self,
        user_id: int,
        start_date: str,
        end_date: str,
        transaction_type: Optional[str] = None,
        include_pending: bool = False
    ) -> List[dict]:
        """Get transactions grouped by category"""
        session = self.session_factory()
        try:
            start_dt = _parse_date(start_date)
            end_dt = _parse_date(end_date)

            query = session.query(
                Transaction.category_id,
                Category.name.label('category_name'),
                func.sum(Transaction.amount).label('total'),
                func.count(Transaction.id).label('count')
            ).join(Category).filter(
                Transaction.user_id == user_id,
                Transaction.deleted_at.is_(None),
                Transaction.event_date >= start_dt,
                Transaction.event_date <= end_dt
            )

            if not include_pending:
                query = query.filter(Transaction.status == TransactionStatus.COMPLETED)

            if transaction_type:
                try:
                    trans_type = TransactionType[transaction_type.upper()]
                    query = query.filter(Transaction.transaction_type == trans_type)
                except KeyError:
                    pass

            results = query.group_by(
                Transaction.category_id,
                Category.name
            ).all()

            return [
                {
                    'category_id': r.category_id,
                    'category_name': r.category_name,
                    'total': round(r.total, 2),
                    'count': r.count
                }
                for r in results
            ]
        finally:
            session.close()
