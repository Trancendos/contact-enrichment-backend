from sqlalchemy.orm import Session
from src.models.contact import Contact
from src.models.contact_history import ContactHistory
from src.models.contact_relationship import ContactRelationship
from src.services.history_service import HistoryService
from datetime import datetime
import json

class ContactManagementService:
    """Manages contact-related operations.

    This service provides methods for creating, updating, deleting,
    splitting, merging, and managing relationships for contacts. It also
    logs all actions to the contact history.
    """
    def __init__(self, db_session: Session, user_id: int):
        self.db_session = db_session
        self.user_id = user_id
        self.history_service = HistoryService(db_session)

    def _log_history(self, contact_id, action, before_data, after_data, request_info=None):
        """Logs a contact history event.

        Args:
            contact_id: The ID of the contact.
            action: The action performed (e.g., 'create', 'update').
            before_data: The contact data before the action.
            after_data: The contact data after the action.
            request_info: Optional information about the request.
        """
        self.history_service.log_action(
            contact_id=contact_id,
            user_id=self.user_id,
            action=action,
            before_data=json.dumps(before_data, default=str),
            after_data=json.dumps(after_data, default=str),
            timestamp=datetime.now(),
            request_info=json.dumps(request_info, default=str) if request_info else None
        )

    def create_contact(self, contact_data: dict, request_info=None):
        """Creates a new contact.

        Args:
            contact_data: A dictionary of contact data.
            request_info: Optional information about the request.

        Returns:
            A dictionary with the result of the operation.
        """
        new_contact = Contact(
            user_id=self.user_id,
            full_name=contact_data.get("full_name"),
            first_name=contact_data.get("first_name"),
            last_name=contact_data.get("last_name"),
            organization=contact_data.get("organization"),
            title=contact_data.get("title"),
            emails=contact_data.get("emails", []),
            phones=contact_data.get("phones", []),
            notes=contact_data.get("notes"),
            tags=contact_data.get("tags", []),
            related_names=contact_data.get("related_names", []),
            explorium_data=contact_data.get("explorium_data"),
        )
        self.db_session.add(new_contact)
        self.db_session.commit()
        self.db_session.refresh(new_contact)
        self._log_history(new_contact.id, "create", {}, new_contact.to_dict(), request_info)
        return {"success": True, "contact": new_contact.to_dict()}

    def update_contact(self, contact_id: int, updated_data: dict, request_info=None):
        """Updates an existing contact.

        Args:
            contact_id: The ID of the contact to update.
            updated_data: A dictionary of updated contact data.
            request_info: Optional information about the request.

        Returns:
            A dictionary with the result of the operation.
        """
        contact = self.db_session.query(Contact).filter_by(id=contact_id, user_id=self.user_id).first()
        if not contact:
            return {"success": False, "error": "Contact not found"}

        before_data = contact.to_dict()

        for key, value in updated_data.items():
            if hasattr(contact, key):
                setattr(contact, key, value)

        self.db_session.commit()
        self.db_session.refresh(contact)
        self._log_history(contact.id, "update", before_data, contact.to_dict(), request_info)
        return {"success": True, "contact": contact.to_dict()}

    def delete_contact(self, contact_id: int, request_info=None):
        """Deletes a contact.

        Args:
            contact_id: The ID of the contact to delete.
            request_info: Optional information about the request.

        Returns:
            A dictionary with the result of the operation.
        """
        contact = self.db_session.query(Contact).filter_by(id=contact_id, user_id=self.user_id).first()
        if not contact:
            return {"success": False, "error": "Contact not found"}

        before_data = contact.to_dict()
        self.db_session.delete(contact)
        self.db_session.commit()
        self._log_history(contact_id, "delete", before_data, {}, request_info)
        return {"success": True, "message": "Contact deleted"}

    def split_phone(self, original_contact_id: int, phone_to_split: dict, request_info=None):
        """Splits a phone number into a new contact.

        Args:
            original_contact_id: The ID of the original contact.
            phone_to_split: The phone number to split.
            request_info: Optional information about the request.

        Returns:
            A dictionary with the result of the operation.
        """
        original_contact = self.db_session.query(Contact).filter_by(id=original_contact_id, user_id=self.user_id).first()
        if not original_contact:
            return {"success": False, "error": "Original contact not found"}

        before_original_data = original_contact.to_dict()

        # Create new contact for the split phone
        new_contact_data = {
            "full_name": original_contact.full_name,
            "first_name": original_contact.first_name,
            "last_name": original_contact.last_name,
            "organization": original_contact.organization,
            "title": original_contact.title,
            "emails": [],
            "phones": [phone_to_split],
            "notes": f"Split from contact ID {original_contact.id}",
            "tags": original_contact.tags,
            "related_names": original_contact.related_names,
            "explorium_data": original_contact.explorium_data,
        }
        new_contact = Contact(
            user_id=self.user_id,
            **new_contact_data
        )
        self.db_session.add(new_contact)
        self.db_session.flush() # To get new_contact.id

        # Remove phone from original contact
        original_contact.phones = [p for p in original_contact.phones if p != phone_to_split]
        self.db_session.commit()
        self.db_session.refresh(original_contact)
        self.db_session.refresh(new_contact)

        self._log_history(original_contact.id, "split_phone_original", before_original_data, original_contact.to_dict(), request_info)
        self._log_history(new_contact.id, "split_phone_new", {}, new_contact.to_dict(), request_info)

        return {"success": True, "new_contact": new_contact.to_dict(), "updated_original": original_contact.to_dict()}

    def split_all(self, original_contact_id: int, request_info=None):
        """Splits all phone numbers and emails into new contacts.

        Args:
            original_contact_id: The ID of the original contact.
            request_info: Optional information about the request.

        Returns:
            A dictionary with the result of the operation.
        """
        original_contact = self.db_session.query(Contact).filter_by(id=original_contact_id, user_id=self.user_id).first()
        if not original_contact:
            return {"success": False, "error": "Original contact not found"}

        before_original_data = original_contact.to_dict()
        new_contacts = []

        # Split by emails
        for email in original_contact.emails:
            if email.get("value"): # Ensure email has a value
                new_contact_data = {
                    "full_name": original_contact.full_name,
                    "first_name": original_contact.first_name,
                    "last_name": original_contact.last_name,
                    "organization": original_contact.organization,
                    "title": original_contact.title,
                    "emails": [email],
                    "phones": [],
                    "notes": f"Split from contact ID {original_contact.id} (email)",
                    "tags": original_contact.tags,
                    "related_names": original_contact.related_names,
                    "explorium_data": original_contact.explorium_data,
                }
                new_contact = Contact(user_id=self.user_id, **new_contact_data)
                self.db_session.add(new_contact)
                new_contacts.append(new_contact)

        # Split by phones
        for phone in original_contact.phones:
            if phone.get("value"): # Ensure phone has a value
                new_contact_data = {
                    "full_name": original_contact.full_name,
                    "first_name": original_contact.first_name,
                    "last_name": original_contact.last_name,
                    "organization": original_contact.organization,
                    "title": original_contact.title,
                    "emails": [],
                    "phones": [phone],
                    "notes": f"Split from contact ID {original_contact.id} (phone)",
                    "tags": original_contact.tags,
                    "related_names": original_contact.related_names,
                    "explorium_data": original_contact.explorium_data,
                }
                new_contact = Contact(user_id=self.user_id, **new_contact_data)
                self.db_session.add(new_contact)
                new_contacts.append(new_contact)

        self.db_session.delete(original_contact)
        self.db_session.commit()

        for nc in new_contacts:
            self.db_session.refresh(nc)
            self._log_history(nc.id, "split_all_new", {}, nc.to_dict(), request_info)
        self._log_history(original_contact.id, "split_all_original_deleted", before_original_data, {}, request_info)

        return {"success": True, "new_contacts": [nc.to_dict() for nc in new_contacts]}

    def merge_contacts(self, contact_ids: list[int], request_info=None):
        """Merges multiple contacts into a single contact.

        Args:
            contact_ids: A list of contact IDs to merge.
            request_info: Optional information about the request.

        Returns:
            A dictionary with the result of the operation.
        """
        contacts_to_merge = self.db_session.query(Contact).filter(Contact.id.in_(contact_ids), Contact.user_id == self.user_id).all()
        if not contacts_to_merge or len(contacts_to_merge) < 2:
            return {"success": False, "error": "At least two contacts are required for merging"}

        # Choose the first contact as the primary contact to merge into
        primary_contact = contacts_to_merge[0]
        other_contacts = contacts_to_merge[1:]

        before_primary_data = primary_contact.to_dict()

        # Merge fields (simple concatenation for now, can be made smarter)
        for other_contact in other_contacts:
            primary_contact.emails.extend([e for e in other_contact.emails if e not in primary_contact.emails])
            primary_contact.phones.extend([p for p in other_contact.phones if p not in primary_contact.phones])
            primary_contact.tags.extend([t for t in other_contact.tags if t not in primary_contact.tags])
            primary_contact.notes = (primary_contact.notes or "") + (f"\nMerged from contact ID {other_contact.id}: {other_contact.notes}" if other_contact.notes else "")
            # You might want to merge other fields like full_name, organization, etc., with more sophisticated logic

        self.db_session.commit()
        self.db_session.refresh(primary_contact)

        self._log_history(primary_contact.id, "merge_primary", before_primary_data, primary_contact.to_dict(), request_info)
        for other_contact in other_contacts:
            self._log_history(other_contact.id, "merge_deleted", other_contact.to_dict(), {}, request_info)
            self.db_session.delete(other_contact)
        self.db_session.commit()

        return {"success": True, "merged_contact": primary_contact.to_dict()}

    def add_relationship(self, contact_id_1: int, contact_id_2: int, relationship_type: str, request_info=None):
        """Adds a relationship between two contacts.

        Args:
            contact_id_1: The ID of the first contact.
            contact_id_2: The ID of the second contact.
            relationship_type: The type of relationship.
            request_info: Optional information about the request.

        Returns:
            A dictionary with the result of the operation.
        """
        if contact_id_1 == contact_id_2:
            return {"success": False, "error": "Cannot create a relationship with self"}

        contact1 = self.db_session.query(Contact).filter_by(id=contact_id_1, user_id=self.user_id).first()
        contact2 = self.db_session.query(Contact).filter_by(id=contact_id_2, user_id=self.user_id).first()

        if not contact1 or not contact2:
            return {"success": False, "error": "One or both contacts not found"}

        # Check if relationship already exists (in either direction)
        existing_rel = self.db_session.query(ContactRelationship).filter(
            ((ContactRelationship.contact_id_1 == contact_id_1) & (ContactRelationship.contact_id_2 == contact_id_2)) |
            ((ContactRelationship.contact_id_1 == contact_id_2) & (ContactRelationship.contact_id_2 == contact_id_1))
        ).first()

        if existing_rel:
            return {"success": False, "error": "Relationship already exists"}

        new_relationship = ContactRelationship(
            contact_id_1=contact_id_1,
            contact_id_2=contact_id_2,
            relationship_type=relationship_type,
            user_id=self.user_id
        )
        self.db_session.add(new_relationship)
        self.db_session.commit()
        self.db_session.refresh(new_relationship)

        self._log_history(contact_id_1, "add_relationship", {}, new_relationship.to_dict(), request_info)
        self._log_history(contact_id_2, "add_relationship", {}, new_relationship.to_dict(), request_info)

        return {"success": True, "relationship": new_relationship.to_dict()}

    def remove_relationship(self, relationship_id: int, request_info=None):
        """Removes a relationship between two contacts.

        Args:
            relationship_id: The ID of the relationship to remove.
            request_info: Optional information about the request.

        Returns:
            A dictionary with the result of the operation.
        """
        relationship = self.db_session.query(ContactRelationship).filter_by(id=relationship_id, user_id=self.user_id).first()
        if not relationship:
            return {"success": False, "error": "Relationship not found"}

        before_data = relationship.to_dict()
        self.db_session.delete(relationship)
        self.db_session.commit()

        self._log_history(relationship.contact_id_1, "remove_relationship", before_data, {}, request_info)
        self._log_history(relationship.contact_id_2, "remove_relationship", before_data, {}, request_info)

        return {"success": True, "message": "Relationship removed"}

    def get_relationships_for_contact(self, contact_id: int):
        """Gets all relationships for a specific contact.

        Args:
            contact_id: The ID of the contact.

        Returns:
            A list of relationships.
        """
        relationships = self.db_session.query(ContactRelationship).filter(
            ((ContactRelationship.contact_id_1 == contact_id) | (ContactRelationship.contact_id_2 == contact_id)) &
            (ContactRelationship.user_id == self.user_id)
        ).all()
        
        result = []
        for rel in relationships:
            related_contact_id = rel.contact_id_1 if rel.contact_id_2 == contact_id else rel.contact_id_2
            related_contact = self.db_session.query(Contact).filter_by(id=related_contact_id).first()
            result.append({
                "id": rel.id,
                "contact_id_1": rel.contact_id_1,
                "contact_id_2": rel.contact_id_2,
                "relationship_type": rel.relationship_type,
                "related_contact_name": related_contact.full_name if related_contact else "Unknown Contact"
            })
        return result

    def get_all_relationships(self):
        """Gets all relationships for the current user.

        Returns:
            A list of all relationships.
        """
        relationships = self.db_session.query(ContactRelationship).filter_by(user_id=self.user_id).all()
        result = []
        for rel in relationships:
            contact1 = self.db_session.query(Contact).filter_by(id=rel.contact_id_1).first()
            contact2 = self.db_session.query(Contact).filter_by(id=rel.contact_id_2).first()
            result.append({
                "id": rel.id,
                "contact_id_1": rel.contact_id_1,
                "contact_id_2": rel.contact_id_2,
                "relationship_type": rel.relationship_type,
                "contact_1_name": contact1.full_name if contact1 else "Unknown Contact",
                "contact_2_name": contact2.full_name if contact2 else "Unknown Contact"
            })
        return result

