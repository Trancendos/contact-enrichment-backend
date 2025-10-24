"""
Contact relationship routes for the Flask application.

This module contains routes for creating, retrieving, updating, and deleting
relationships between contacts.
"""
from flask import Blueprint, request, jsonify, session, g
from src.services.relationship_service import RelationshipService
from src.middleware.auth_middleware import login_required

relationship_bp = Blueprint("relationship_bp", __name__)


@relationship_bp.route("/relationships", methods=["POST"])
@login_required
def create_relationship():
    """
    Create a new relationship between two contacts.

    This route expects a JSON body with 'contact_id_1', 'contact_id_2', and
    'relationship_type' fields.

    Returns:
        A JSON response with the newly created relationship, or an error
        message if creation fails.
    """
    user_id = session.get("user_id")
    data = request.json
    contact_id_1 = data.get("contact_id_1")
    contact_id_2 = data.get("contact_id_2")
    relationship_type = data.get("relationship_type")
    description = data.get("description")

    if not all([contact_id_1, contact_id_2, relationship_type]):
        return jsonify({"success": False, "error": "Missing required fields"}), 400

    try:
        service = RelationshipService(g.db, user_id)
        relationship = service.create_relationship(contact_id_1, contact_id_2, relationship_type, description)
        return jsonify({"success": True, "relationship": relationship.to_dict()}), 201
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400
    except Exception as e:
        g.db.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


@relationship_bp.route("/relationships/<string:contact_id>", methods=["GET"])
@login_required
def get_relationships_for_contact(contact_id):
    """
    Get all relationships for a specific contact.

    Args:
        contact_id (str): The ID of the contact to get relationships for.

    Returns:
        A JSON response with a list of relationships for the contact.
    """
    user_id = session.get("user_id")

    try:
        service = RelationshipService(g.db, user_id)
        relationships = service.get_relationships_for_contact(contact_id)
        return jsonify({"success": True, "relationships": [r.to_dict() for r in relationships]}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@relationship_bp.route("/relationships/<int:relationship_id>", methods=["PUT"])
@login_required
def update_relationship(relationship_id):
    """
    Update an existing relationship.

    This route expects a JSON body with 'relationship_type' and/or
    'description' fields.

    Args:
        relationship_id (int): The ID of the relationship to update.

    Returns:
        A JSON response with the updated relationship, or an error message if
        the update fails.
    """
    user_id = session.get("user_id")
    data = request.json
    new_type = data.get("relationship_type")
    new_description = data.get("description")

    if not new_type and not new_description:
        return jsonify({"success": False, "error": "No update data provided"}), 400

    try:
        service = RelationshipService(g.db, user_id)
        relationship = service.update_relationship(relationship_id, new_type, new_description)
        return jsonify({"success": True, "relationship": relationship.to_dict()}), 200
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400
    except Exception as e:
        g.db.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


@relationship_bp.route("/relationships/<int:relationship_id>", methods=["DELETE"])
@login_required
def delete_relationship(relationship_id):
    """
    Delete a relationship.

    Args:
        relationship_id (int): The ID of the relationship to delete.

    Returns:
        A JSON response with a success message, or an error message if
        deletion fails.
    """
    user_id = session.get("user_id")

    try:
        service = RelationshipService(g.db, user_id)
        result = service.delete_relationship(relationship_id)
        return jsonify({"success": True, "message": result["message"]}), 200
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400
    except Exception as e:
        g.db.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

