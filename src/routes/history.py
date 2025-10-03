from flask import Blueprint, request, jsonify, session, g
from src.services.history_service import HistoryService
from src.middleware.auth_middleware import login_required

history_bp = Blueprint("history", __name__)

@history_bp.route("/api/history/contact/<contact_id>", methods=["GET"])
@login_required
def get_contact_history(contact_id):
    """Get history for a specific contact"""
    user_id = g.user_id
    try:
        service = HistoryService(g.db, user_id)
        limit = request.args.get("limit", 50, type=int)
        history = service.get_contact_history(contact_id, limit)
        
        return jsonify({
            "success": True,
            "history": history
        })
    
    except Exception as e:
        print(f"Error in get_contact_history: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@history_bp.route("/api/history/user", methods=["GET"])
@login_required
def get_user_history():
    """Get all history for the current user"""
    user_id = g.user_id
    try:
        service = HistoryService(g.db, user_id)
        limit = request.args.get("limit", 100, type=int)
        history = service.get_user_history(limit)
        
        return jsonify({
            "success": True,
            "history": history
        })
    
    except Exception as e:
        print(f"Error in get_user_history: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@history_bp.route("/api/history/recent", methods=["GET"])
@login_required
def get_recent_actions():
    """Get recent actions for the current user"""
    user_id = g.user_id
    try:
        service = HistoryService(g.db, user_id)
        action_types = request.args.getlist("action_types")
        limit = request.args.get("limit", 20, type=int)
        
        history = service.get_recent_actions(
            action_types if action_types else None, 
            limit
        )
        
        return jsonify({
            "success": True,
            "history": history
        })
    
    except Exception as e:
        print(f"Error in get_recent_actions: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@history_bp.route("/api/history/undo/<int:history_id>", methods=["POST"])
@login_required
def undo_action(history_id):
    """Undo a specific action"""
    user_id = g.user_id
    try:
        service = HistoryService(g.db, user_id)
        result = service.undo_action(history_id)
        
        if result["success"]:
            return jsonify(result)
        else:
            return jsonify(result), 400
    
    except Exception as e:
        print(f"Error in undo_action: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@history_bp.route("/api/backup/create", methods=["POST"])
@login_required
def create_backup():
    """Create a backup of all contacts"""
    user_id = g.user_id
    try:
        service = HistoryService(g.db, user_id)
        data = request.get_json()
        contacts_data = data.get("contacts", [])
        
        if not contacts_data:
            return jsonify({"success": False, "error": "No contacts data provided"}), 400
        
        backup = service.create_backup(contacts_data)
        
        if backup:
            return jsonify({
                "success": True,
                "backup": backup
            })
        else:
            return jsonify({"success": False, "error": "Failed to create backup"}), 500
    
    except Exception as e:
        print(f"Error in create_backup: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@history_bp.route("/api/backup/list", methods=["GET"])
@login_required
def list_backups():
    """List all backups for the current user"""
    user_id = g.user_id
    try:
        service = HistoryService(g.db, user_id)
        limit = request.args.get("limit", 10, type=int)
        backups = service.get_backups(limit)
        
        return jsonify({
            "success": True,
            "backups": backups
        })
    
    except Exception as e:
        print(f"Error in list_backups: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@history_bp.route("/api/backup/restore/<int:backup_id>", methods=["POST"])
@login_required
def restore_backup(backup_id):
    """Restore contacts from a backup"""
    user_id = g.user_id
    try:
        service = HistoryService(g.db, user_id)
        result = service.restore_backup(backup_id)
        
        if result["success"]:
            return jsonify(result)
        else:
            return jsonify(result), 400
    
    except Exception as e:
        print(f"Error in restore_backup: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

