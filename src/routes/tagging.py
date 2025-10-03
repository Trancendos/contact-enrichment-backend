from flask import Blueprint, request, jsonify
from src.services.ai_tagging_service import AITaggingService

tagging_bp = Blueprint('tagging', __name__)
ai_tagging_service = AITaggingService()

@tagging_bp.route('/api/suggest_tags', methods=['POST'])
def suggest_tags():
    """Suggest tags for a contact using AI"""
    try:
        data = request.get_json()
        contact = data.get('contact')
        
        if not contact:
            return jsonify({'success': False, 'error': 'No contact data provided'}), 400
        
        suggested_tags = ai_tagging_service.suggest_tags(contact)
        
        return jsonify({
            'success': True,
            'suggested_tags': suggested_tags
        })
    
    except Exception as e:
        print(f"Error in suggest_tags: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@tagging_bp.route('/api/suggest_tags_batch', methods=['POST'])
def suggest_tags_batch():
    """Suggest tags for multiple contacts using AI"""
    try:
        data = request.get_json()
        contacts = data.get('contacts')
        
        if not contacts:
            return jsonify({'success': False, 'error': 'No contacts data provided'}), 400
        
        results = ai_tagging_service.suggest_tags_batch(contacts)
        
        return jsonify({
            'success': True,
            'suggestions': results
        })
    
    except Exception as e:
        print(f"Error in suggest_tags_batch: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
