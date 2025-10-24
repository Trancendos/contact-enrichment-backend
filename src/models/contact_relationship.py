from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.models.base import Base

class ContactRelationship(Base):
    """Represents a relationship between two contacts."""
    __tablename__ = 'contact_relationships'

    id: int = Column(Integer, primary_key=True, index=True)  # The unique identifier for the relationship.
    user_id: int = Column(Integer, ForeignKey('users.id'), nullable=False)  # The ID of the user who owns this relationship.
    contact_id_1: str = Column(String, ForeignKey('contacts.id'), nullable=False)  # The ID of the first contact in the relationship.
    contact_id_2: str = Column(String, ForeignKey('contacts.id'), nullable=False)  # The ID of the second contact in the relationship.
    relationship_type: str = Column(String, nullable=False)  # The type of relationship (e.g., 'colleague', 'family').
    description: str = Column(Text, nullable=True)  # A description of the relationship.
    created_at: DateTime = Column(DateTime, server_default=func.now())  # The timestamp when the relationship was created.
    updated_at: DateTime = Column(DateTime, onupdate=func.now())  # The timestamp when the relationship was last updated.
    contact1 = relationship('Contact', foreign_keys=[contact_id_1], backref='relationships_as_contact1')
    contact2 = relationship('Contact', foreign_keys=[contact_id_2], backref='relationships_as_contact2')
    user = relationship('User', back_populates='contact_relationships')

    def __repr__(self):
        return f"<ContactRelationship(id={self.id}, contact_id_1='{self.contact_id_1}', contact_id_2='{self.contact_id_2}', type='{self.relationship_type}')>"

