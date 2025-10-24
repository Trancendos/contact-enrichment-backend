"""
Contact management routes for the Flask application.

This module contains routes for creating, updating, deleting, splitting, and
merging contacts.
"""
from flask import Blueprint, request, jsonify, session, g
from src.services.contact_management_service import ContactManagementService
from src.middleware.auth_middleware import login_required

contact_management_bp = Blueprint("contact_management", __name__)


@contact_management_bp.route("/contacts", methods=["POST"])
@login_required
def create_contact():
    """
    Create a new contact.

    This route expects a JSON body with the contact's information.

    Returns:
        A JSON response with the newly created contact, or an error message if
        creation fails.
    """
    user_id = g.user_id
    contact_data = request.get_json()
    service = ContactManagementService(g.db, user_id)
    result = service.create_contact(contact_data, request)
    return jsonify(result)

@contact_management_bp.route("/contacts/<contact_id>", methods=["PUT"])
@login_required
def update_contact(contact_id):
    """
    Update an existing contact.

    This route expects a JSON body with the updated contact information.

    Args:
        contact_id (str): The ID of the contact to update.

    Returns:
        A JSON response with the updated contact, or an error message if
        the update fails.
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
    """
    Delete a contact.

    Args:
        contact_id (str): The ID of the contact to delete.

    Returns:
        A JSON response with a success message, or an error message if
        deletion fails.
    """
    user_id = g.user_id
    service = ContactManagementService(g.db, user_id)
    result = service.delete_contact(contact_id, request)
    return jsonify(result)

@contact_management_bp.route("/contacts/split_phone", methods=["POST"])
@login_required
def split_phone():
    """
    Split a phone number from a contact into a new contact.

    This route expects a JSON body with 'original_contact_id' and
    'phone_to_split' fields.

    Returns:
        A JSON response with the new contact, or an error message if the
        operation fails.
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
    """
    Split all phone numbers from a contact into new contacts.

    This route expects a JSON body with an 'original_contact_id' field.

    Returns:
        A JSON response with a list of new contacts, or an error message if
        the operation fails.
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
    """
    Merge multiple contacts into a single contact.

    This route expects a JSON body with a 'contact_ids' field, which is a
    list of contact IDs to merge.

    Returns:
        A JSON response with the merged contact, or an error message if the
        operation fails.
    """
    user_id = g.user_id
    data = request.get_json()
    contact_ids = data.get("contact_ids")
    
    service = ContactManagementService(g.db, user_id)
    result = service.merge_contacts(contact_ids, request)
    return jsonify(result)

