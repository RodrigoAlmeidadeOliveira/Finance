"""
API endpoints for manual transaction management (cash flow).
"""
from flask import Blueprint, request, jsonify, current_app
from functools import wraps

from ..services.transaction_service import TransactionService
from ..database import get_session
from .auth import token_required


transactions_bp = Blueprint('transactions', __name__, url_prefix='/api/transactions')


def get_transaction_service() -> TransactionService:
    """Factory for TransactionService"""
    return TransactionService(session_factory=get_session)


@transactions_bp.route('/', methods=['POST'])
@token_required
def create_transaction(user):
    """
    Create a new manual transaction.

    Request body:
    {
        "event_date": "2025-12-23T10:00:00",
        "transaction_type": "INCOME" | "EXPENSE",
        "category_id": 1,
        "amount": 1500.00,
        "description": "Salary payment",
        "effective_date": "2025-12-23T10:00:00",  // optional
        "institution_id": 1,  // optional
        "credit_card_id": 1,  // optional
        "notes": "...",  // optional
        "status": "PENDING" | "COMPLETED",  // optional, default PENDING
        "is_recurring": false  // optional
    }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'Request body is required'}), 400

        # Required fields
        required = ['event_date', 'transaction_type', 'category_id', 'amount', 'description']
        missing = [f for f in required if f not in data]
        if missing:
            return jsonify({'error': f'Missing required fields: {", ".join(missing)}'}), 400

        service = get_transaction_service()
        transaction = service.create_transaction(
            user_id=user['id'],
            event_date=data['event_date'],
            transaction_type=data['transaction_type'],
            category_id=data['category_id'],
            amount=data['amount'],
            description=data['description'],
            effective_date=data.get('effective_date'),
            institution_id=data.get('institution_id'),
            credit_card_id=data.get('credit_card_id'),
            notes=data.get('notes'),
            status=data.get('status', 'PENDING'),
            is_recurring=data.get('is_recurring', False)
        )

        return jsonify(transaction), 201

    except ValueError as e:
        current_app.logger.error(f"Validation error creating transaction: {e}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error creating transaction: {e}", exc_info=True)
        return jsonify({'error': 'Failed to create transaction'}), 500


@transactions_bp.route('/', methods=['GET'])
@token_required
def list_transactions(user):
    """
    List transactions with filters.

    Query parameters:
    - start_date: ISO format date (e.g., 2025-01-01)
    - end_date: ISO format date
    - transaction_type: INCOME or EXPENSE
    - category_id: integer
    - institution_id: integer
    - credit_card_id: integer
    - status: PENDING or COMPLETED
    - min_amount: float
    - max_amount: float
    - search: text search in description/notes
    - include_deleted: boolean (default false)
    - limit: int (default 100, max 500)
    - offset: int (default 0)

    Response:
    {
        "items": [...],
        "total": 150,
        "limit": 100,
        "offset": 0
    }
    """
    try:
        # Parse query parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        transaction_type = request.args.get('transaction_type')
        category_id = request.args.get('category_id', type=int)
        institution_id = request.args.get('institution_id', type=int)
        credit_card_id = request.args.get('credit_card_id', type=int)
        status = request.args.get('status')
        min_amount = request.args.get('min_amount', type=float)
        max_amount = request.args.get('max_amount', type=float)
        search = request.args.get('search')
        include_deleted = request.args.get('include_deleted', 'false').lower() == 'true'
        limit = min(request.args.get('limit', type=int, default=100), 500)
        offset = request.args.get('offset', type=int, default=0)

        service = get_transaction_service()
        result = service.list_transactions(
            user_id=user['id'],
            start_date=start_date,
            end_date=end_date,
            transaction_type=transaction_type,
            category_id=category_id,
            institution_id=institution_id,
            credit_card_id=credit_card_id,
            status=status,
            min_amount=min_amount,
            max_amount=max_amount,
            search=search,
            include_deleted=include_deleted,
            limit=limit,
            offset=offset
        )

        return jsonify(result), 200

    except Exception as e:
        current_app.logger.error(f"Error listing transactions: {e}", exc_info=True)
        return jsonify({'error': 'Failed to list transactions'}), 500


@transactions_bp.route('/<int:transaction_id>', methods=['GET'])
@token_required
def get_transaction(user, transaction_id):
    """Get a single transaction by ID"""
    try:
        service = get_transaction_service()
        transaction = service.get_transaction(transaction_id, user['id'])

        if not transaction:
            return jsonify({'error': 'Transaction not found'}), 404

        return jsonify(transaction), 200

    except Exception as e:
        current_app.logger.error(f"Error getting transaction: {e}", exc_info=True)
        return jsonify({'error': 'Failed to get transaction'}), 500


@transactions_bp.route('/<int:transaction_id>', methods=['PUT'])
@token_required
def update_transaction(user, transaction_id):
    """
    Update transaction fields.

    Request body (all fields optional):
    {
        "event_date": "2025-12-23T10:00:00",
        "effective_date": "2025-12-23T10:00:00",
        "transaction_type": "INCOME" | "EXPENSE",
        "category_id": 1,
        "amount": 1500.00,
        "description": "Updated description",
        "notes": "...",
        "institution_id": 1,
        "credit_card_id": 1,
        "status": "PENDING" | "COMPLETED",
        "is_recurring": false
    }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'Request body is required'}), 400

        service = get_transaction_service()
        transaction = service.update_transaction(
            transaction_id,
            user['id'],
            **data
        )

        return jsonify(transaction), 200

    except ValueError as e:
        current_app.logger.error(f"Validation error updating transaction: {e}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error updating transaction: {e}", exc_info=True)
        return jsonify({'error': 'Failed to update transaction'}), 500


@transactions_bp.route('/<int:transaction_id>', methods=['DELETE'])
@token_required
def delete_transaction(user, transaction_id):
    """
    Delete transaction (soft delete by default).

    Query parameters:
    - hard: boolean (default false) - if true, permanently delete
    """
    try:
        hard_delete = request.args.get('hard', 'false').lower() == 'true'

        service = get_transaction_service()
        success = service.delete_transaction(
            transaction_id,
            user['id'],
            soft=not hard_delete
        )

        if not success:
            return jsonify({'error': 'Transaction not found'}), 404

        return jsonify({'message': 'Transaction deleted successfully'}), 200

    except Exception as e:
        current_app.logger.error(f"Error deleting transaction: {e}", exc_info=True)
        return jsonify({'error': 'Failed to delete transaction'}), 500


@transactions_bp.route('/<int:transaction_id>/complete', methods=['POST'])
@token_required
def mark_completed(user, transaction_id):
    """Mark transaction as completed"""
    try:
        service = get_transaction_service()
        transaction = service.mark_as_completed(transaction_id, user['id'])

        return jsonify(transaction), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        current_app.logger.error(f"Error marking transaction as completed: {e}", exc_info=True)
        return jsonify({'error': 'Failed to update transaction'}), 500


@transactions_bp.route('/<int:transaction_id>/pending', methods=['POST'])
@token_required
def mark_pending(user, transaction_id):
    """Mark transaction as pending"""
    try:
        service = get_transaction_service()
        transaction = service.mark_as_pending(transaction_id, user['id'])

        return jsonify(transaction), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        current_app.logger.error(f"Error marking transaction as pending: {e}", exc_info=True)
        return jsonify({'error': 'Failed to update transaction'}), 500


@transactions_bp.route('/bulk-update-status', methods=['POST'])
@token_required
def bulk_update_status(user):
    """
    Update status for multiple transactions.

    Request body:
    {
        "transaction_ids": [1, 2, 3, 4],
        "status": "COMPLETED" | "PENDING"
    }
    """
    try:
        data = request.get_json()

        if not data or 'transaction_ids' not in data or 'status' not in data:
            return jsonify({'error': 'transaction_ids and status are required'}), 400

        service = get_transaction_service()
        count = service.bulk_update_status(
            data['transaction_ids'],
            user['id'],
            data['status']
        )

        return jsonify({'updated': count}), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error bulk updating: {e}", exc_info=True)
        return jsonify({'error': 'Failed to update transactions'}), 500


@transactions_bp.route('/<int:transaction_id>/duplicate', methods=['POST'])
@token_required
def duplicate_transaction(user, transaction_id):
    """
    Duplicate transaction to a new date (for recurring transactions).

    Request body:
    {
        "new_event_date": "2026-01-23T10:00:00",
        "link_as_recurrence": true  // optional, default true
    }
    """
    try:
        data = request.get_json()

        if not data or 'new_event_date' not in data:
            return jsonify({'error': 'new_event_date is required'}), 400

        service = get_transaction_service()
        new_transaction = service.duplicate_transaction(
            transaction_id,
            user['id'],
            data['new_event_date'],
            data.get('link_as_recurrence', True)
        )

        return jsonify(new_transaction), 201

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error duplicating transaction: {e}", exc_info=True)
        return jsonify({'error': 'Failed to duplicate transaction'}), 500


@transactions_bp.route('/summary', methods=['GET'])
@token_required
def get_summary(user):
    """
    Get financial summary for a period.

    Query parameters:
    - start_date: ISO format (required)
    - end_date: ISO format (required)
    - include_pending: boolean (default false)

    Response:
    {
        "period": {
            "start": "2025-01-01T00:00:00",
            "end": "2025-12-31T23:59:59"
        },
        "income": 50000.00,
        "expense": 30000.00,
        "balance": 20000.00,
        "transaction_count": 245,
        "income_count": 50,
        "expense_count": 195
    }
    """
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        include_pending = request.args.get('include_pending', 'false').lower() == 'true'

        if not start_date or not end_date:
            return jsonify({'error': 'start_date and end_date are required'}), 400

        service = get_transaction_service()
        summary = service.get_summary(
            user['id'],
            start_date,
            end_date,
            include_pending
        )

        return jsonify(summary), 200

    except Exception as e:
        current_app.logger.error(f"Error getting summary: {e}", exc_info=True)
        return jsonify({'error': 'Failed to get summary'}), 500


@transactions_bp.route('/monthly-summary/<int:year>/<int:month>', methods=['GET'])
@token_required
def get_monthly_summary(user, year, month):
    """
    Get summary for a specific month.

    Query parameters:
    - include_pending: boolean (default false)
    """
    try:
        if not (1 <= month <= 12):
            return jsonify({'error': 'Invalid month (must be 1-12)'}), 400

        include_pending = request.args.get('include_pending', 'false').lower() == 'true'

        service = get_transaction_service()
        summary = service.get_monthly_summary(
            user['id'],
            year,
            month,
            include_pending
        )

        return jsonify(summary), 200

    except Exception as e:
        current_app.logger.error(f"Error getting monthly summary: {e}", exc_info=True)
        return jsonify({'error': 'Failed to get monthly summary'}), 500


@transactions_bp.route('/by-category', methods=['GET'])
@token_required
def get_by_category(user):
    """
    Get transactions grouped by category.

    Query parameters:
    - start_date: ISO format (required)
    - end_date: ISO format (required)
    - transaction_type: INCOME or EXPENSE (optional)
    - include_pending: boolean (default false)

    Response:
    [
        {
            "category_id": 1,
            "category_name": "Salary",
            "total": 5000.00,
            "count": 1
        },
        ...
    ]
    """
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        transaction_type = request.args.get('transaction_type')
        include_pending = request.args.get('include_pending', 'false').lower() == 'true'

        if not start_date or not end_date:
            return jsonify({'error': 'start_date and end_date are required'}), 400

        service = get_transaction_service()
        by_category = service.get_by_category(
            user['id'],
            start_date,
            end_date,
            transaction_type,
            include_pending
        )

        return jsonify(by_category), 200

    except Exception as e:
        current_app.logger.error(f"Error getting by category: {e}", exc_info=True)
        return jsonify({'error': 'Failed to get transactions by category'}), 500
