from flask import Blueprint, request, jsonify, session, g
from src.services.contact_management_service import ContactManagementService
from src.middleware.auth_middleware import login_required

contact_management_bp = Blueprint("contact_management", __name__)

@contact_management_bp.route("/contacts", methods=["POST"])
@login_required
def create_contact():
    user_id = g.user_id
    contact_data = request.get_json()
    service = ContactManagementService(g.db, user_id)
    result = service.create_contact(contact_data, request)
    return jsonify(result)

@contact_management_bp.route("/contacts/<contact_id>", methods=["PUT"])
@login_required
def update_contact(contact_id):
    user_id = g.user_id
    data = request.get_json()
    updated_data = data.get("updated_data")
    
    service = ContactManagementService(g.db, user_id)
    result = service.update_contact(contact_id, updated_data, request)
    return jsonify(result)

@contact_management_bp.route("/contacts/<contact_id>", methods=["DELETE"])
@login_required
def delete_contact(contact_id):
    user_id = g.user_id
    service = ContactManagementService(g.db, user_id)
    result = service.delete_contact(contact_id, request)
    return jsonify(result)

@contact_management_bp.route("/contacts/split_phone", methods=["POST"])
@login_required
def split_phone():
    user_id = g.user_id
    data = request.get_json()
    original_contact_id = data.get("original_contact_id")
    phone_to_split = data.get("phone_to_split")
    
    service = ContactManagementService(g.db, user_id)
    result = service.split_phone(original_contact_id, phone_to_split, request)
    return jsonify(result)

@contact_management_bp.route("/contacts/split_all", methods=["POST"])
@login_required
def split_all():
    user_id = g.user_id
    data = request.get_json()
    original_contact_id = data.get("original_contact_id")
    
    service = ContactManagementService(g.db, user_id)
    result = service.split_all(original_contact_id, request)
    return jsonify(result)

@contact_management_bp.route("/contacts/merge", methods=["POST"])
@login_required
def merge_contacts():
    user_id = g.user_id
    data = request.get_json()
    contact_ids = data.get("contact_ids")
    
    service = ContactManagementService(g.db, user_id)
    result = service.merge_contacts(contact_ids, request)
    return jsonify(result)

