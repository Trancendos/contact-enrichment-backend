from flask import Blueprint, request, jsonify
from src.services.explorium_service import enrich_contact_with_explorium

enrichment_bp = Blueprint("enrichment", __name__)

@enrichment_bp.route("/enrich_contact", methods=["POST"])
def enrich_contact():
    data = request.get_json()
    contact = data.get("contact")

    if not contact:
        return jsonify({"error": "Contact data is required for enrichment"}), 400

    enriched_data = enrich_contact_with_explorium(contact)

    if enriched_data.get("error"):
        return jsonify({"error": "Failed to enrich contact", "details": enriched_data["error"]}), 500

    return jsonify({"success": True, "enriched_data": enriched_data})

