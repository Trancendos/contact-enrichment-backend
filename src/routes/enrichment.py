"""
Contact enrichment routes for the Flask application.

This module contains routes for enriching contact information using external
services like Explorium.
"""
from flask import Blueprint, request, jsonify, g
from src.services.explorium_service import ExploriumService
from src.middleware.auth_middleware import login_required

enrichment_bp = Blueprint("enrichment", __name__)


@enrichment_bp.route("/enrich_contact", methods=["POST"])
@login_required
def enrich_contact():
    """
    Enrich a contact's information.

    This route expects a JSON body with a 'contact' object. It uses the
    Explorium service to enrich the contact's data.

    Returns:
        A JSON response with the enriched contact data, or an error message if
        enrichment fails.
    """
    user_id = g.user_id # Assuming user_id is set in g by login_required
    data = request.get_json()
    contact = data.get("contact")

    if not contact:
        return jsonify({"error": "Contact data is required for enrichment"}), 400

    try:
        service = ExploriumService(g.db, user_id)
        enriched_data = service.enrich_contact_with_explorium(contact)

        if enriched_data.get("error"):
            return jsonify({"error": "Failed to enrich contact", "details": enriched_data["error"]}), 500

        return jsonify({"success": True, "enriched_data": enriched_data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

