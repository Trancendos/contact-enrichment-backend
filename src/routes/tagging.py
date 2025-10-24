"""
AI-powered tagging routes for the Flask application.

This module contains routes for suggesting tags for single or multiple
contacts using an AI tagging service.
"""
from flask import Blueprint, request, jsonify, session, g
from src.services.ai_tagging_service import AITaggingService
from src.middleware.auth_middleware import login_required

tagging_bp = Blueprint("tagging", __name__)


@tagging_bp.route("/api/suggest_tags", methods=["POST"])
@login_required
def suggest_tags():
    """
    Suggest tags for a contact using AI.

    This route expects a JSON body with a 'contact' object.

    Returns:
        A JSON response with a list of suggested tags.
    """
    user_id = g.user_id
    try:
        data = request.get_json()
        contact = data.get("contact")
        
        if not contact:
            return jsonify({"success": False, "error": "No contact data provided"}), 400
        
        ai_tagging_service = AITaggingService(g.db, user_id)
        suggested_tags = ai_tagging_service.suggest_tags(contact)
        
        return jsonify({
            "success": True,
            "suggested_tags": suggested_tags
        })
    
    except Exception as e:
        print(f"Error in suggest_tags: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@tagging_bp.route("/api/suggest_tags_batch", methods=["POST"])
@login_required
def suggest_tags_batch():
    """
    Suggest tags for multiple contacts using AI.

    This route expects a JSON body with a 'contacts' field, which is a list
    of contact objects.

    Returns:
        A JSON response with a list of suggestions for each contact.
    """
    user_id = g.user_id
    try:
        data = request.get_json()
        contacts = data.get("contacts")
        
        if not contacts:
            return jsonify({"success": False, "error": "No contacts data provided"}), 400
        
        ai_tagging_service = AITaggingService(g.db, user_id)
        results = ai_tagging_service.suggest_tags_batch(contacts)
        
        return jsonify({
            "success": True,
            "suggestions": results
        })
    
    except Exception as e:
        print(f"Error in suggest_tags_batch: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

