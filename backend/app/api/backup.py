"""
API endpoints for backup and export operations.
"""
import json
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app, send_file
from io import BytesIO

from ..services.backup_service import BackupService
from ..database import get_session
from .auth import token_required


backup_bp = Blueprint('backup', __name__, url_prefix='/api/backup')


def get_backup_service() -> BackupService:
    """Factory for BackupService"""
    return BackupService(session_factory=get_session)


@backup_bp.route('/export/json', methods=['GET'])
@token_required
def export_json(user):
    """
    Export complete user data as JSON backup.

    Response: JSON file download with all user data
    """
    try:
        service = get_backup_service()
        backup_data = service.export_full_backup(user['id'])

        # Create JSON string with pretty formatting
        json_str = json.dumps(backup_data, indent=2, ensure_ascii=False)

        # Create filename with timestamp
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f'flow_forecaster_backup_{user["id"]}_{timestamp}.json'

        # Return as downloadable file
        return send_file(
            BytesIO(json_str.encode('utf-8')),
            mimetype='application/json',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        current_app.logger.error(f"Error exporting JSON backup: {e}", exc_info=True)
        return jsonify({'error': 'Failed to export backup'}), 500


@backup_bp.route('/export/excel', methods=['GET'])
@token_required
def export_excel(user):
    """
    Export user data as Excel file (XLSX).

    Response: Excel file download with data in multiple sheets
    """
    try:
        service = get_backup_service()
        excel_bytes = service.export_to_excel(user['id'])

        # Create filename with timestamp
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f'flow_forecaster_data_{user["id"]}_{timestamp}.xlsx'

        # Return as downloadable file
        return send_file(
            BytesIO(excel_bytes),
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )

    except ImportError:
        return jsonify({'error': 'Excel export not available. Missing openpyxl library.'}), 500
    except Exception as e:
        current_app.logger.error(f"Error exporting Excel: {e}", exc_info=True)
        return jsonify({'error': 'Failed to export Excel file'}), 500


@backup_bp.route('/import', methods=['POST'])
@token_required
def import_backup(user):
    """
    Restore data from JSON backup.

    Request:
    - JSON file upload or JSON body
    - Query param: overwrite=true (optional, DANGEROUS - deletes existing data)

    Response:
    {
        "success": true,
        "statistics": {
            "categories": 15,
            "institutions": 3,
            "transactions": 245,
            ...
        },
        "errors": []
    }
    """
    try:
        overwrite = request.args.get('overwrite', 'false').lower() == 'true'

        # Get backup data from request
        if request.is_json:
            backup_data = request.get_json()
        elif 'file' in request.files:
            file = request.files['file']
            if not file.filename.endswith('.json'):
                return jsonify({'error': 'Only JSON files are supported'}), 400
            try:
                backup_data = json.load(file)
            except json.JSONDecodeError:
                return jsonify({'error': 'Invalid JSON file'}), 400
        else:
            return jsonify({'error': 'No backup data provided. Send JSON body or file upload.'}), 400

        # Validate backup format
        if not backup_data.get('metadata') or not backup_data.get('data'):
            return jsonify({'error': 'Invalid backup format'}), 400

        # Warning for overwrite
        if overwrite:
            current_app.logger.warning(f"User {user['id']} is performing OVERWRITE restore")

        service = get_backup_service()
        stats = service.import_full_backup(
            user['id'],
            backup_data,
            overwrite=overwrite
        )

        return jsonify({
            'success': True,
            'statistics': stats,
            'message': 'Backup restored successfully'
        }), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error importing backup: {e}", exc_info=True)
        return jsonify({'error': 'Failed to import backup'}), 500


@backup_bp.route('/summary', methods=['GET'])
@token_required
def get_backup_summary(user):
    """
    Get summary of what would be exported (without actually exporting).

    Useful for showing user what data exists before download.

    Response:
    {
        "user_id": 1,
        "statistics": {
            "categories": 15,
            "institutions": 3,
            "transactions": 245,
            ...
        },
        "estimated_size_kb": 1024
    }
    """
    try:
        service = get_backup_service()
        backup_data = service.export_full_backup(user['id'])

        # Calculate estimated size
        json_str = json.dumps(backup_data)
        size_kb = len(json_str.encode('utf-8')) / 1024

        return jsonify({
            'user_id': user['id'],
            'statistics': backup_data['metadata']['statistics'],
            'estimated_size_kb': round(size_kb, 2),
            'export_date': backup_data['metadata']['export_date']
        }), 200

    except Exception as e:
        current_app.logger.error(f"Error getting backup summary: {e}", exc_info=True)
        return jsonify({'error': 'Failed to get backup summary'}), 500


@backup_bp.route('/validate', methods=['POST'])
@token_required
def validate_backup(user):
    """
    Validate a backup file before importing.

    Request: JSON file upload or JSON body

    Response:
    {
        "valid": true,
        "version": "1.0",
        "export_date": "2025-12-23T...",
        "statistics": {...},
        "warnings": [],
        "errors": []
    }
    """
    try:
        # Get backup data
        if request.is_json:
            backup_data = request.get_json()
        elif 'file' in request.files:
            file = request.files['file']
            try:
                backup_data = json.load(file)
            except json.JSONDecodeError:
                return jsonify({
                    'valid': False,
                    'errors': ['Invalid JSON format']
                }), 200
        else:
            return jsonify({'error': 'No backup data provided'}), 400

        errors = []
        warnings = []

        # Check metadata
        if not backup_data.get('metadata'):
            errors.append('Missing metadata section')
        else:
            metadata = backup_data['metadata']
            if metadata.get('format') != 'flow_forecaster_backup':
                warnings.append('Unknown backup format')
            if not metadata.get('version'):
                warnings.append('Missing version information')

        # Check data section
        if not backup_data.get('data'):
            errors.append('Missing data section')

        # Check statistics match
        if backup_data.get('metadata', {}).get('statistics'):
            stats = backup_data['metadata']['statistics']
            data = backup_data.get('data', {})

            for entity, count in stats.items():
                actual_count = len(data.get(entity, []))
                if actual_count != count:
                    warnings.append(
                        f'{entity}: expected {count} items, found {actual_count}'
                    )

        return jsonify({
            'valid': len(errors) == 0,
            'version': backup_data.get('metadata', {}).get('version'),
            'export_date': backup_data.get('metadata', {}).get('export_date'),
            'statistics': backup_data.get('metadata', {}).get('statistics', {}),
            'warnings': warnings,
            'errors': errors
        }), 200

    except Exception as e:
        current_app.logger.error(f"Error validating backup: {e}", exc_info=True)
        return jsonify({
            'valid': False,
            'errors': [str(e)]
        }), 200
