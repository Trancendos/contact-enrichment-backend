from sqlalchemy.orm import Session
from src.models.contact_relationship import ContactRelationship
from src.models.contact import Contact
from src.models.user import User
from src.services.history_service import HistoryService

class RelationshipService:
    """Manages relationships between contacts."""
    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id
        self.history_service = HistoryService(db, user_id)

    def create_relationship(self, contact_id_1: str, contact_id_2: str, relationship_type: str, description: str = None):
        """Creates a new relationship between two contacts.

        Args:
            contact_id_1: The ID of the first contact.
            contact_id_2: The ID of the second contact.
            relationship_type: The type of relationship.
            description: An optional description of the relationship.

        Returns:
            The newly created ContactRelationship object.
        """
        if contact_id_1 == contact_id_2:
            raise ValueError("Cannot create a relationship with the same contact.")

        contact1 = self.db.query(Contact).filter(Contact.id == contact_id_1, Contact.user_id == self.user_id).first()
        contact2 = self.db.query(Contact).filter(Contact.id == contact_id_2, Contact.user_id == self.user_id).first()

        if not contact1 or not contact2:
            raise ValueError("One or both contacts not found or do not belong to the user.")

        # Check for existing relationship (bidirectional)
        existing_relationship = self.db.query(ContactRelationship).filter(
            ((ContactRelationship.contact_id_1 == contact_id_1 and ContactRelationship.contact_id_2 == contact_id_2) or
             (ContactRelationship.contact_id_1 == contact_id_2 and ContactRelationship.contact_id_2 == contact_id_1))
            and ContactRelationship.user_id == self.user_id
        ).first()

        if existing_relationship:
            raise ValueError("Relationship already exists between these contacts.")

        relationship = ContactRelationship(
            user_id=self.user_id,
            contact_id_1=contact_id_1,
            contact_id_2=contact_id_2,
            relationship_type=relationship_type,
            description=description
        )
        self.db.add(relationship)
        self.db.commit()
        self.db.refresh(relationship)

        self.history_service.log_action(
            action_type="create_relationship",
            contact_id=contact_id_1, # Log against contact1, could be both
            description=f"Created relationship ‘{relationship_type}’ with {contact2.full_name}",
            after_data=relationship.to_dict() # Assuming to_dict() method exists or will be added
        )
        self.history_service.log_action(
            action_type="create_relationship",
            contact_id=contact_id_2, # Log against contact2
            description=f"Created relationship ‘{relationship_type}’ with {contact1.full_name}",
            after_data=relationship.to_dict()
        )

        return relationship

    def get_relationships_for_contact(self, contact_id: str):
        """Gets all relationships for a specific contact.

        Args:
            contact_id: The ID of the contact.

        Returns:
            A list of ContactRelationship objects.
        """
        relationships = self.db.query(ContactRelationship).filter(
            ((ContactRelationship.contact_id_1 == contact_id) | (ContactRelationship.contact_id_2 == contact_id))
            & (ContactRelationship.user_id == self.user_id)
        ).all()
        return relationships

    def delete_relationship(self, relationship_id: int):
        """Deletes a relationship.

        Args:
            relationship_id: The ID of the relationship to delete.

        Returns:
            A dictionary with a success message.
        """
        relationship = self.db.query(ContactRelationship).filter(
            ContactRelationship.id == relationship_id,
            ContactRelationship.user_id == self.user_id
        ).first()

        if not relationship:
            raise ValueError("Relationship not found or does not belong to the user.")

        before_data = relationship.to_dict() # Assuming to_dict() method exists or will be added
        contact1_id = relationship.contact_id_1
        contact2_id = relationship.contact_id_2

        self.db.delete(relationship)
        self.db.commit()

        contact1 = self.db.query(Contact).filter(Contact.id == contact1_id, Contact.user_id == self.user_id).first()
        contact2 = self.db.query(Contact).filter(Contact.id == contact2_id, Contact.user_id == self.user_id).first()

        self.history_service.log_action(
            action_type="delete_relationship",
            contact_id=contact1_id,
            description=f"Deleted relationship ‘{relationship.relationship_type}’ with {contact2.full_name if contact2 else 'another contact'}",
            before_data=before_data
        )
        self.history_service.log_action(
            action_type="delete_relationship",
            contact_id=contact2_id,
            description=f"Deleted relationship ‘{relationship.relationship_type}’ with {contact1.full_name if contact1 else 'another contact'}",
            before_data=before_data
        )

        return {"message": "Relationship deleted successfully"}

    def update_relationship(self, relationship_id: int, new_type: str = None, new_description: str = None):
        """Updates a relationship.

        Args:
            relationship_id: The ID of the relationship to update.
            new_type: The new relationship type.
            new_description: The new description.

        Returns:
            The updated ContactRelationship object.
        """
        relationship = self.db.query(ContactRelationship).filter(
            ContactRelationship.id == relationship_id,
            ContactRelationship.user_id == self.user_id
        ).first()

        if not relationship:
            raise ValueError("Relationship not found or does not belong to the user.")

        before_data = relationship.to_dict()

        if new_type:
            relationship.relationship_type = new_type
        if new_description:
            relationship.description = new_description

        self.db.commit()
        self.db.refresh(relationship)

        contact1 = self.db.query(Contact).filter(Contact.id == relationship.contact_id_1, Contact.user_id == self.user_id).first()
        contact2 = self.db.query(Contact).filter(Contact.id == relationship.contact_id_2, Contact.user_id == self.user_id).first()

        self.history_service.log_action(
            action_type="update_relationship",
            contact_id=relationship.contact_id_1,
            description=f"Updated relationship ‘{relationship.relationship_type}’ with {contact2.full_name if contact2 else 'another contact'}",
            before_data=before_data,
            after_data=relationship.to_dict()
        )
        self.history_service.log_action(
            action_type="update_relationship",
            contact_id=relationship.contact_id_2,
            description=f"Updated relationship ‘{relationship.relationship_type}’ with {contact1.full_name if contact1 else 'another contact'}",
            before_data=before_data,
            after_data=relationship.to_dict()
        )

        return relationship


# Add to_dict() method to ContactRelationship model for serialization
def _contact_relationship_to_dict(self):
    return {
        "id": self.id,
        "user_id": self.user_id,
        "contact_id_1": self.contact_id_1,
        "contact_id_2": self.contact_id_2,
        "relationship_type": self.relationship_type,
        "description": self.description,
        "created_at": self.created_at.isoformat() if self.created_at else None,
        "updated_at": self.updated_at.isoformat() if self.updated_at else None,
    }

ContactRelationship.to_dict = _contact_relationship_to_dict

# Add to_dict() method to Contact model for serialization if not already present
# This is needed for history logging
if not hasattr(Contact, 'to_dict'):
    def _contact_to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "full_name": self.full_name,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "organization": self.organization,
            "title": self.title,
            "emails": self.emails,
            "phones": self.phones,
            "notes": self.notes,
            "tags": self.tags,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    Contact.to_dict = _contact_to_dict

