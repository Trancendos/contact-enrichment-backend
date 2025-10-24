"""
SQLAlchemy model for a relationship between two contacts.
"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.models.base import Base


class ContactRelationship(Base):
    """
    Represents a relationship between two contacts.

    Attributes:
        id (int): The unique identifier for the relationship.
        user_id (int): The ID of the user who owns this relationship.
        contact_id_1 (str): The ID of the first contact in the relationship.
        contact_id_2 (str): The ID of the second contact in the relationship.
        relationship_type (str): The type of relationship (e.g., 'colleague', 'family', 'friend').
        description (str): A description of the relationship.
        created_at (datetime): The timestamp when the relationship was created.
        updated_at (datetime): The timestamp when the relationship was last updated.
        contact1 (Contact): The first contact in the relationship.
        contact2 (Contact): The second contact in the relationship.
        user (User): The user who owns this relationship.
    """
    __tablename__ = 'contact_relationships'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    contact_id_1 = Column(String, ForeignKey('contacts.id'), nullable=False)
    contact_id_2 = Column(String, ForeignKey('contacts.id'), nullable=False)
    relationship_type = Column(String, nullable=False)  # e.g., 'colleague', 'family', 'friend'
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    # Define relationships to Contact model
    contact1 = relationship('Contact', foreign_keys=[contact_id_1], backref='relationships_as_contact1')
    contact2 = relationship('Contact', foreign_keys=[contact_id_2], backref='relationships_as_contact2')
    user = relationship('User', back_populates='contact_relationships')

    def __repr__(self):
        """
        Return a string representation of the ContactRelationship object.

        Returns:
            str: A string representation of the ContactRelationship object.
        """
        return f"<ContactRelationship(id={self.id}, contact_id_1='{self.contact_id_1}', contact_id_2='{self.contact_id_2}', type='{self.relationship_type}')>"

