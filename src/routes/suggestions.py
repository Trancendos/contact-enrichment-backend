"""
AI-powered suggestion routes for the Flask application.

This module contains routes for generating, listing, approving, and rejecting
contact suggestions.
"""
from flask import Blueprint, request, jsonify, session, g
from src.models.suggestion import Suggestion
from src.models.contact import Contact
from src.services.ai_predictor import predictor
from src.services.nlu_service import nlu_service
from src.services.explorium_service import ExploriumService
import random

suggestions_bp = Blueprint("suggestions", __name__)


def generate_ai_suggestions(contacts, user_id, db_session):
    """
    Generate AI-powered suggestions for contacts.

    This function uses various services to generate suggestions for a list of
    contacts. It uses the NLU service to analyze contact notes, the Explorium
    service to enrich contact data, and an AI predictor to suggest splitting
    or merging contacts.

    Args:
        contacts (list): A list of contact dictionaries to generate suggestions for.
        user_id (int): The ID of the user who owns the contacts.
        db_session (sqlalchemy.orm.Session): The database session.

    Returns:
        list: A list of Suggestion objects.
    """
    suggestions = []
    explorium_service_instance = ExploriumService(db_session, user_id)

    for contact in contacts:
        contact_id = contact.get("id")
        
        # 1. NLU Analysis of notes
        if contact.get("notes"):
            analysis = nlu_service.analyze_note(contact["notes"])
            nlu_suggestions = nlu_service.generate_suggestions_from_analysis(contact, analysis)
            for nlu_sugg in nlu_suggestions:
                suggestion = Suggestion(
                    user_id=user_id,
                    contact_id=contact_id,
                    field_name=nlu_sugg["field"],
                    current_value=contact.get(nlu_sugg["field"], ""),
                    suggested_value=nlu_sugg["value"],
                    confidence=nlu_sugg["confidence"],
                    source=nlu_sugg["source"],
                    status="pending"
                )
                suggestions.append(suggestion)
        
        # 2. Explorium Enrichment and Suggestions
        company_name = contact.get("organization")
        email = next((e.get("value") for e in contact.get("emails", []) if e.get("value")), None)
        full_name = contact.get("full_name")

        if company_name or email or full_name:
            explorium_enriched_data = explorium_service_instance.enrich_contact_with_explorium(contact)
            
            if explorium_enriched_data:
                # Suggest updating company name if Explorium finds a more accurate one
                if "explorium_business_data" in explorium_enriched_data and \
                   explorium_enriched_data["explorium_business_data"].get("name") and \
                   explorium_enriched_data["explorium_business_data"]["name"].lower() != company_name.lower():
                    suggestions.append(Suggestion(
                        user_id=user_id,
                        contact_id=contact_id,
                        field_name="organization",
                        current_value=company_name,
                        suggested_value=explorium_enriched_data["explorium_business_data"]["name"],
                        confidence=0.95,
                        source="Explorium - Business Name Update",
                        status="pending"
                    ))
                
                # Suggest enriching with prospect data (e.g., job title, LinkedIn URL)
                if "explorium_prospect_data" in explorium_enriched_data:
                    prospect_data = explorium_enriched_data["explorium_prospect_data"]
                    if prospect_data.get("job_title") and prospect_data["job_title"] != contact.get("title"):
                        suggestions.append(Suggestion(
                            user_id=user_id,
                            contact_id=contact_id,
                            field_name="title",
                            current_value=contact.get("title", ""),
                            suggested_value=prospect_data["job_title"],
                            confidence=0.90,
                            source="Explorium - Job Title Enrichment",
                            status="pending"
                        ))
                    if prospect_data.get("linkedin_url") and prospect_data["linkedin_url"] not in [url.get("value") for url in contact.get("url", [])]:
                        suggestions.append(Suggestion(
                            user_id=user_id,
                            contact_id=contact_id,
                            field_name="url",
                            current_value=contact.get("url", ""),
                            suggested_value=prospect_data["linkedin_url"],
                            confidence=0.0,
                            source="Explorium - LinkedIn URL Enrichment",
                            status="pending"
                        ))

        # 3. Check if contact should be split
        split_probability = predictor.calculate_split_probability(contact)
        if split_probability > 0.6:
            suggestions.append(Suggestion(
                user_id=user_id,
                contact_id=contact_id,
                field_name="action",
                current_value="merged_contact",
                suggested_value="split_contact",
                confidence=split_probability,
                source="AI Predictor - Split Analysis (Multiple emails/phones detected)",
                status="pending"
            ))
    
    # 4. Check for potential merges between contacts
    all_contacts = db_session.query(Contact).filter(Contact.user_id == user_id).all()
    for i, contact1 in enumerate(all_contacts):
        for contact2 in all_contacts[i+1:]:
            merge_probability = predictor.calculate_merge_probability(contact1.to_dict(), contact2.to_dict())
            if merge_probability > 0.5:
                suggestions.append(Suggestion(
                    user_id=user_id,
                    contact_id=contact1.id,
                    field_name="action",
                    current_value=f"separate_contacts_{contact1.id}_{contact2.id}",
                    suggested_value=f"merge_with_{contact2.full_name}",
                    confidence=merge_probability,
                    source="AI Predictor - Merge Analysis (Similar contact detected)",
                    status="pending"
                ))
    
    return suggestions

@suggestions_bp.route("/analyze", methods=["POST"])
def analyze_contacts():
    """
    Analyze contacts and generate suggestions.

    This route expects a JSON body with a 'contacts' field, which is a list
    of contact objects to analyze. It clears any existing pending suggestions
    for the user and then generates new ones.

    Returns:
        A JSON response with a success message and the number of suggestions
        generated.
    """
    user_id = session.get("user_id")
    
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    data = request.get_json()
    contacts = data.get("contacts", [])
    
    if not contacts:
        return jsonify({"error": "No contacts provided"}), 400
    
    # Clear existing pending suggestions for this user
    g.db.query(Suggestion).filter_by(user_id=user_id, status="pending").delete()
    
    # Generate AI-powered suggestions
    suggestions = generate_ai_suggestions(contacts, user_id, g.db)
    
    # Save to database
    for suggestion in suggestions:
        g.db.add(suggestion)
    
    g.db.commit()
    
    return jsonify({
        "success": True,
        "message": f"Generated {len(suggestions)} suggestions",
        "suggestions_count": len(suggestions)
    })


@suggestions_bp.route("/list", methods=["GET"])
def list_suggestions():
    """
    Get all pending suggestions for the current user.

    This route accepts an optional 'status' query parameter to filter the
    suggestions.

    Returns:
        A JSON response with a list of suggestions.
    """
    user_id = session.get("user_id")
    
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    status = request.args.get("status", "pending")
    
    suggestions = g.db.query(Suggestion).filter_by(user_id=user_id, status=status).all()
    
    return jsonify({
        "success": True,
        "suggestions": [s.to_dict() for s in suggestions]
    })

@suggestions_bp.route("/<int:suggestion_id>/approve", methods=["POST"])
def approve_suggestion(suggestion_id):
    """
    Approve a suggestion and learn from feedback.

    Args:
        suggestion_id (int): The ID of the suggestion to approve.

    Returns:
        A JSON response with a success message and the approved suggestion.
    """
    user_id = session.get("user_id")
    
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    suggestion = g.db.query(Suggestion).filter_by(id=suggestion_id, user_id=user_id).first()
    
    if not suggestion:
        return jsonify({"error": "Suggestion not found"}), 404
    
    # Learn from approval
    if suggestion.field_name == "action":
        if "split" in suggestion.suggested_value.lower():
            predictor.learn_from_feedback("split", {"confidence": suggestion.confidence}, approved=True)
        elif "merge" in suggestion.suggested_value.lower():
            predictor.learn_from_feedback("merge", {"confidence": suggestion.confidence}, approved=True)
    
    suggestion.status = "approved"
    g.db.commit()
    
    return jsonify({
        "success": True,
        "message": "Suggestion approved and learned",
        "suggestion": suggestion.to_dict()
    })


@suggestions_bp.route("/<int:suggestion_id>/reject", methods=["POST"])
def reject_suggestion(suggestion_id):
    """
    Reject a suggestion and learn from feedback.

    Args:
        suggestion_id (int): The ID of the suggestion to reject.

    Returns:
        A JSON response with a success message and the rejected suggestion.
    """
    user_id = session.get("user_id")
    
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    suggestion = g.db.query(Suggestion).filter_by(id=suggestion_id, user_id=user_id).first()
    
    if not suggestion:
        return jsonify({"error": "Suggestion not found"}), 404
    
    # Learn from rejection
    if suggestion.field_name == "action":
        if "split" in suggestion.suggested_value.lower():
            predictor.learn_from_feedback("split", {"confidence": suggestion.confidence}, approved=False)
        elif "merge" in suggestion.suggested_value.lower():
            predictor.learn_from_feedback("merge", {"confidence": suggestion.confidence}, approved=False)
    
    suggestion.status = "rejected"
    g.db.commit()
    
    return jsonify({
        "success": True,
        "message": "Suggestion rejected and learned",
        "suggestion": suggestion.to_dict()
    })

@suggestions_bp.route("/bulk_action", methods=["POST"])
def bulk_action():
    """
    Approve or reject multiple suggestions at once.

    This route expects a JSON body with a 'suggestion_ids' field (a list of
    suggestion IDs) and an 'action' field ('approve' or 'reject').

    Returns:
        A JSON response with a success message and the number of suggestions
        affected.
    """
    user_id = session.get("user_id")
    
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    data = request.get_json()
    suggestion_ids = data.get("suggestion_ids", [])
    action = data.get("action")  # "approve" or "reject"
    
    if not suggestion_ids or action not in ["approve", "reject"]:
        return jsonify({"error": "Invalid request"}), 400
    
    status = "approved" if action == "approve" else "rejected"
    
    suggestions = g.db.query(Suggestion).filter(
        Suggestion.id.in_(suggestion_ids),
        Suggestion.user_id == user_id
    ).all()
    
    for suggestion in suggestions:
        suggestion.status = status
    
    g.db.commit()
    
    return jsonify({
        "success": True,
        "message": f"{len(suggestions)} suggestions {status}",
        "count": len(suggestions)
    })

