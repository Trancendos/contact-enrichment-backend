from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base

class Suggestion(Base):
    """Represents a suggestion for improving contact data."""
    __tablename__ = 'suggestions'

    id: int = Column(Integer, primary_key=True)  # The unique identifier for the suggestion.
    user_id: int = Column(Integer, ForeignKey('users.id'), nullable=False)  # The ID of the user who owns this suggestion.
    contact_id: str = Column(String, nullable=False)  # The ID of the contact this suggestion is for.
    field_name: str = Column(String(100), nullable=False)  # The name of the field the suggestion is for.
    current_value: str = Column(String(500), nullable=True)  # The current value of the field.
    suggested_value: str = Column(String(500), nullable=False)  # The suggested new value for the field.
    confidence: float = Column(Float, nullable=False)  # The confidence score of the suggestion.
    source: str = Column(String(255), nullable=False)  # The source of the suggestion (e.g., 'AI', 'NLU').
    status: str = Column(String(50), default='pending')  # The status of the suggestion (e.g., 'pending', 'accepted').
    created_at: DateTime = Column(DateTime, server_default=func.now())  # The timestamp when the suggestion was created.
    updated_at: DateTime = Column(DateTime, onupdate=func.now())  # The timestamp when the suggestion was last updated.

    user = relationship('User', backref='suggestions')

    def __repr__(self):
        return f'<Suggestion {self.id} for contact {self.contact_id}>'

    def to_dict(self):
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

