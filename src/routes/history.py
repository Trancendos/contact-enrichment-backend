from flask import Blueprint, request, jsonify, session
from src.services.history_service import HistoryService

history_bp = Blueprint('history', __name__)

@history_bp.route('/api/history/contact/<contact_id>', methods=['GET'])
def get_contact_history(contact_id):
    """Get history for a specific contact"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': 'Not authenticated'}), 401
        
        limit = request.args.get('limit', 50, type=int)
        history = HistoryService.get_contact_history(user_id, contact_id, limit)
        
        return jsonify({
            'success': True,
            'history': history
        })
    
    except Exception as e:
        print(f"Error in get_contact_history: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@history_bp.route('/api/history/user', methods=['GET'])
def get_user_history():
    """Get all history for the current user"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': 'Not authenticated'}), 401
        
        limit = request.args.get('limit', 100, type=int)
        history = HistoryService.get_user_history(user_id, limit)
        
        return jsonify({
            'success': True,
            'history': history
        })
    
    except Exception as e:
        print(f"Error in get_user_history: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@history_bp.route('/api/history/recent', methods=['GET'])
def get_recent_actions():
    """Get recent actions for the current user"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': 'Not authenticated'}), 401
        
        action_types = request.args.getlist('action_types')
        limit = request.args.get('limit', 20, type=int)
        
        history = HistoryService.get_recent_actions(
            user_id, 
            action_types if action_types else None, 
            limit
        )
        
        return jsonify({
            'success': True,
            'history': history
        })
    
    except Exception as e:
        print(f"Error in get_recent_actions: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@history_bp.route('/api/history/undo/<int:history_id>', methods=['POST'])
def undo_action(history_id):
    """Undo a specific action"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': 'Not authenticated'}), 401
        
        result = HistoryService.undo_action(user_id, history_id)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
    
    except Exception as e:
        print(f"Error in undo_action: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@history_bp.route('/api/backup/create', methods=['POST'])
def create_backup():
    """Create a backup of all contacts"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': 'Not authenticated'}), 401
        
        data = request.get_json()
        contacts_data = data.get('contacts', [])
        
        if not contacts_data:
            return jsonify({'success': False, 'error': 'No contacts data provided'}), 400
        
        backup = HistoryService.create_backup(user_id, contacts_data)
        
        if backup:
            return jsonify({
                'success': True,
                'backup': backup
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to create backup'}), 500
    
    except Exception as e:
        print(f"Error in create_backup: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@history_bp.route('/api/backup/list', methods=['GET'])
def list_backups():
    """List all backups for the current user"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': 'Not authenticated'}), 401
        
        limit = request.args.get('limit', 10, type=int)
        backups = HistoryService.get_backups(user_id, limit)
        
        return jsonify({
            'success': True,
            'backups': backups
        })
    
    except Exception as e:
        print(f"Error in list_backups: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@history_bp.route('/api/backup/restore/<int:backup_id>', methods=['POST'])
def restore_backup(backup_id):
    """Restore contacts from a backup"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': 'Not authenticated'}), 401
        
        # Get the backup
        from src.models.contact_history import ContactHistory
        import json
        
        backup = ContactHistory.query.filter_by(
            id=backup_id,
            user_id=user_id,
            action_type='backup'
        ).first()
        
        if not backup:
            return jsonify({'success': False, 'error': 'Backup not found'}), 404
        
        if not backup.after_data:
            return jsonify({'success': False, 'error': 'Backup data not available'}), 400
        
        contacts_data = json.loads(backup.after_data)
        
        return jsonify({
            'success': True,
            'contacts': contacts_data,
            'backup_timestamp': backup.timestamp.isoformat()
        })
    
    except Exception as e:
        print(f"Error in restore_backup: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
