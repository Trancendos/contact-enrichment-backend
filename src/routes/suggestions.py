from flask import Blueprint, request, jsonify, session
from src.models.user import db
from src.models.suggestion import Suggestion
from src.services.ai_predictor import predictor
from src.services.nlu_service import nlu_service
from src.services import explorium_service
import random

suggestions_bp = Blueprint("suggestions", __name__)

def generate_ai_suggestions(contacts, user_id):
    """Generate AI-powered suggestions for contacts using predictor, NLU, and Explorium data"""
    suggestions = []
    
    for contact in contacts:
        contact_id = contact.get("id")
        
        # 1. NLU Analysis of notes
        if contact.get("note"):
            analysis = nlu_service.analyze_note(contact["note"])
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
        company_name = contact.get("org")
        email = next((e.get("value") for e in contact.get("email", []) if e.get("value")), None)
        full_name = contact.get("fn")

        if company_name or email or full_name:
            explorium_enriched_data = explorium_service.enrich_contact_with_explorium(contact)
            
            if explorium_enriched_data:
                # Suggest updating company name if Explorium finds a more accurate one
                if "explorium_business_data" in explorium_enriched_data and \
                   explorium_enriched_data["explorium_business_data"].get("name") and \
                   explorium_enriched_data["explorium_business_data"]["name"].lower() != company_name.lower():
                    suggestions.append(Suggestion(
                        user_id=user_id,
                        contact_id=contact_id,
                        field_name="org",
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
    for i, contact1 in enumerate(contacts):
        for contact2 in contacts[i+1:]:
            merge_probability = predictor.calculate_merge_probability(contact1, contact2)
            if merge_probability > 0.5:
                suggestions.append(Suggestion(
                    user_id=user_id,
                    contact_id=contact1.get("id"),
                    field_name="action",
                    current_value=f"separate_contacts_{contact1.get('id')}_{contact2.get('id')}",
                    suggested_value=f"merge_with_{contact2.get('fullName', 'Unknown')}",
                    confidence=merge_probability,
                    source="AI Predictor - Merge Analysis (Similar contact detected)",
                    status="pending"
                ))
    
    return suggestions

@suggestions_bp.route("/analyze", methods=["POST"])
def analyze_contacts():
    """Analyze contacts and generate suggestions"""
    user_id = session.get("user_id")
    
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    data = request.get_json()
    contacts = data.get("contacts", [])
    
    if not contacts:
        return jsonify({"error": "No contacts provided"}), 400
    
    # Clear existing pending suggestions for this user
    Suggestion.query.filter_by(user_id=user_id, status="pending").delete()
    
    # Generate AI-powered suggestions
    suggestions = generate_ai_suggestions(contacts, user_id)
    
    # Save to database
    for suggestion in suggestions:
        db.session.add(suggestion)
    
    db.session.commit()
    
    return jsonify({
        "success": True,
        "message": f"Generated {len(suggestions)} suggestions",
        "suggestions_count": len(suggestions)
    })

@suggestions_bp.route("/list", methods=["GET"])
def list_suggestions():
    """Get all pending suggestions for the current user"""
    user_id = session.get("user_id")
    
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    status = request.args.get("status", "pending")
    
    suggestions = Suggestion.query.filter_by(user_id=user_id, status=status).all()
    
    return jsonify({
        "success": True,
        "suggestions": [s.to_dict() for s in suggestions]
    })

@suggestions_bp.route("/<int:suggestion_id>/approve", methods=["POST"])
def approve_suggestion(suggestion_id):
    """Approve a suggestion and learn from feedback"""
    user_id = session.get("user_id")
    
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    suggestion = Suggestion.query.filter_by(id=suggestion_id, user_id=user_id).first()
    
    if not suggestion:
        return jsonify({"error": "Suggestion not found"}), 404
    
    # Learn from approval
    if suggestion.field_name == "action":
        if "split" in suggestion.suggested_value.lower():
            predictor.learn_from_feedback("split", {"confidence": suggestion.confidence}, approved=True)
        elif "merge" in suggestion.suggested_value.lower():
            predictor.learn_from_feedback("merge", {"confidence": suggestion.confidence}, approved=True)
    
    suggestion.status = "approved"
    db.session.commit()
    
    return jsonify({
        "success": True,
        "message": "Suggestion approved and learned",
        "suggestion": suggestion.to_dict()
    })

@suggestions_bp.route("/<int:suggestion_id>/reject", methods=["POST"])
def reject_suggestion(suggestion_id):
    """Reject a suggestion and learn from feedback"""
    user_id = session.get("user_id")
    
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    suggestion = Suggestion.query.filter_by(id=suggestion_id, user_id=user_id).first()
    
    if not suggestion:
        return jsonify({"error": "Suggestion not found"}), 404
    
    # Learn from rejection
    if suggestion.field_name == "action":
        if "split" in suggestion.suggested_value.lower():
            predictor.learn_from_feedback("split", {"confidence": suggestion.confidence}, approved=False)
        elif "merge" in suggestion.suggested_value.lower():
            predictor.learn_from_feedback("merge", {"confidence": suggestion.confidence}, approved=False)
    
    suggestion.status = "rejected"
    db.session.commit()
    
    return jsonify({
        "success": True,
        "message": "Suggestion rejected and learned",
        "suggestion": suggestion.to_dict()
    })

@suggestions_bp.route("/bulk_action", methods=["POST"])
def bulk_action():
    """Approve or reject multiple suggestions at once"""
    user_id = session.get("user_id")
    
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    data = request.get_json()
    suggestion_ids = data.get("suggestion_ids", [])
    action = data.get("action")  # "approve" or "reject"
    
    if not suggestion_ids or action not in ["approve", "reject"]:
        return jsonify({"error": "Invalid request"}), 400
    
    status = "approved" if action == "approve" else "rejected"
    
    suggestions = Suggestion.query.filter(
        Suggestion.id.in_(suggestion_ids),
        Suggestion.user_id == user_id
    ).all()
    
    for suggestion in suggestions:
        suggestion.status = status
    
    db.session.commit()
    
    return jsonify({
        "success": True,
        "message": f"{len(suggestions)} suggestions {status}",
        "count": len(suggestions)
    })

