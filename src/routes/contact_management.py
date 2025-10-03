from flask import Blueprint, request, jsonify, session
from src.services.contact_management_service import ContactManagementService

contact_management_bp = Blueprint("contact_management", __name__)

@contact_management_bp.route("/contacts", methods=["POST"])
def create_contact():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    contact_data = request.get_json()
    result = ContactManagementService.create_contact(user_id, contact_data, request)
    return jsonify(result)

@contact_management_bp.route("/contacts/<contact_id>", methods=["PUT"])
def update_contact(contact_id):
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    data = request.get_json()
    before_data = data.get("before_data")
    after_data = data.get("after_data")
    
    result = ContactManagementService.update_contact(user_id, contact_id, before_data, after_data, request)
    return jsonify(result)

@contact_management_bp.route("/contacts/<contact_id>", methods=["DELETE"])
def delete_contact(contact_id):
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    contact_data = request.get_json().get("contact_data")
    result = ContactManagementService.delete_contact(user_id, contact_id, contact_data, request)
    return jsonify(result)

@contact_management_bp.route("/contacts/split_phone", methods=["POST"])
def split_phone():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    data = request.get_json()
    original_contact = data.get("original_contact")
    phone_to_split = data.get("phone_to_split")
    
    result = ContactManagementService.split_phone(user_id, original_contact, phone_to_split, request)
    return jsonify(result)

@contact_management_bp.route("/contacts/split_all", methods=["POST"])
def split_all():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    data = request.get_json()
    original_contact = data.get("original_contact")
    
    result = ContactManagementService.split_all(user_id, original_contact, request)
    return jsonify(result)

@contact_management_bp.route("/contacts/merge", methods=["POST"])
def merge_contacts():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    data = request.get_json()
    contacts_to_merge = data.get("contacts_to_merge")
    
    result = ContactManagementService.merge_contacts(user_id, contacts_to_merge, request)
    return jsonify(result)

