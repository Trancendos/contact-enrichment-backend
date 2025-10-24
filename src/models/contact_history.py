from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base

class ContactHistory(Base):
    """Represents the history of changes to a contact."""
    __tablename__ = 'contact_history'

    id: int = Column(Integer, primary_key=True)  # The unique identifier for the history entry.
    user_id: int = Column(Integer, ForeignKey('users.id'), nullable=False)  # The ID of the user who made the change.
    contact_id: str = Column(String, nullable=False)  # The ID of the contact that was changed.
    action_type: str = Column(String(50), nullable=False)  # The type of action that was performed.
    timestamp: DateTime = Column(DateTime, server_default=func.now(), nullable=False)  # The timestamp when the change was made.
    before_data: str = Column(Text, nullable=True)  # The contact data before the change (JSON string).
    after_data: str = Column(Text, nullable=True)  # The contact data after the change (JSON string).
    description: str = Column(String(500), nullable=True)  # A human-readable description of the change.
    ip_address: str = Column(String(50), nullable=True)  # The IP address of the user who made the change.
    user_agent: str = Column(String(500), nullable=True)  # The user agent of the user who made the change.

    user = relationship('User', back_populates='contact_histories')

    def __repr__(self):
        return f'<ContactHistory {self.id}: {self.action_type} on {self.contact_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'contact_id': self.contact_id,
            'action_type': self.action_type,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'description': self.description,
            'before_data': self.before_data,
            'after_data': self.after_data
        }

