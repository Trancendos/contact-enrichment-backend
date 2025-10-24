from flask import Blueprint, request, jsonify, session, g
from src.services.contact_management_service import ContactManagementService
from src.middleware.auth_middleware import login_required

contact_management_bp = Blueprint("contact_management", __name__)

@contact_management_bp.route("/contacts", methods=["POST"])
@login_required
def create_contact():
    """Creates a new contact.

    Handles the creation of a new contact by processing the provided
    contact data.

    Returns:
        A JSON response with the result of the contact creation.
    """
    user_id = g.user_id
    contact_data = request.get_json()
    service = ContactManagementService(g.db, user_id)
    result = service.create_contact(contact_data, request)
    return jsonify(result)

@contact_management_bp.route("/contacts/<contact_id>", methods=["PUT"])
@login_required
def update_contact(contact_id):
    """Updates an existing contact.

    Args:
        contact_id: The ID of the contact to update.

    Returns:
        A JSON response with the result of the update operation.
    """
    user_id = g.user_id
    data = request.get_json()
    updated_data = data.get("updated_data")
    
    service = ContactManagementService(g.db, user_id)
    result = service.update_contact(contact_id, updated_data, request)
    return jsonify(result)

@contact_management_bp.route("/contacts/<contact_id>", methods=["DELETE"])
@login_required
def delete_contact(contact_id):
    """Deletes a contact.

    Args:
        contact_id: The ID of the contact to delete.

    Returns:
        A JSON response with the result of the deletion.
    """
    user_id = g.user_id
    service = ContactManagementService(g.db, user_id)
    result = service.delete_contact(contact_id, request)
    return jsonify(result)

@contact_management_bp.route("/contacts/split_phone", methods=["POST"])
@login_required
def split_phone():
    """Splits a phone number from a contact into a new contact.

    Returns:
        A JSON response with the result of the split operation.
    """
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
    """Splits all phone numbers from a contact into new contacts.

    Returns:
        A JSON response with the result of the split operation.
    """
    user_id = g.user_id
    data = request.get_json()
    original_contact_id = data.get("original_contact_id")
    
    service = ContactManagementService(g.db, user_id)
    result = service.split_all(original_contact_id, request)
    return jsonify(result)

@contact_management_bp.route("/contacts/merge", methods=["POST"])
@login_required
def merge_contacts():
    """Merges multiple contacts into a single contact.

    Returns:
        A JSON response with the result of the merge operation.
    """
    user_id = g.user_id
    data = request.get_json()
    contact_ids = data.get("contact_ids")
    
    service = ContactManagementService(g.db, user_id)
    result = service.merge_contacts(contact_ids, request)
    return jsonify(result)

