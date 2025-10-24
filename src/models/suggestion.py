"""
SQLAlchemy model for a suggestion.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base


class Suggestion(Base):
    """
    Represents a suggestion for updating a contact's information.

    Attributes:
        id (int): The unique identifier for the suggestion.
        user_id (int): The ID of the user who owns this suggestion.
        contact_id (str): The ID of the contact this suggestion is for.
        field_name (str): The name of the contact field to be updated.
        current_value (str): The current value of the field.
        suggested_value (str): The suggested new value for the field.
        confidence (float): The confidence score of the suggestion.
        source (str): The source of the suggestion (e.g., 'user', 'ai').
        status (str): The status of the suggestion (e.g., 'pending', 'accepted', 'rejected').
        created_at (datetime): The timestamp when the suggestion was created.
        updated_at (datetime): The timestamp when the suggestion was last updated.
        user (User): The user who owns this suggestion.
    """
    __tablename__ = 'suggestions'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    contact_id = Column(String, nullable=False)  # UUID of the contact
    field_name = Column(String(100), nullable=False)
    current_value = Column(String(500), nullable=True)
    suggested_value = Column(String(500), nullable=False)
    confidence = Column(Float, nullable=False)
    source = Column(String(255), nullable=False)
    status = Column(String(50), default='pending')
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    user = relationship('User', backref='suggestions')

    def __repr__(self):
        """
        Return a string representation of the Suggestion object.

        Returns:
            str: A string representation of the Suggestion object.
        """
        return f'<Suggestion {self.id} for contact {self.contact_id}>'

    def to_dict(self):
        """
        Convert the Suggestion object to a dictionary.

        Returns:
            dict: A dictionary representation of the Suggestion object.
        """
        return {
            'id': self.id,
            'user_id': self.user_id,
            'contact_id': self.contact_id,
            'field_name': self.field_name,
            'current_value': self.current_value,
            'suggested_value': self.suggested_value,
            'confidence': self.confidence,
            'source': self.source,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

