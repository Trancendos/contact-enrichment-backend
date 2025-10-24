"""
SQLAlchemy model for contact history.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base


class ContactHistory(Base):
    """
    Represents the history of actions taken on a contact.

    Attributes:
        id (int): The unique identifier for the history record.
        user_id (int): The ID of the user who performed the action.
        contact_id (str): The ID of the contact that was modified.
        action_type (str): The type of action performed (e.g., 'create', 'update', 'delete').
        timestamp (datetime): The timestamp when the action was performed.
        before_data (str): A JSON string representing the contact data before the change.
        after_data (str): A JSON string representing the contact data after the change.
        description (str): A description of the action.
        ip_address (str): The IP address of the user who performed the action.
        user_agent (str): The user agent of the user who performed the action.
        user (User): The user who performed the action.
    """
    __tablename__ = 'contact_history'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    contact_id = Column(String, nullable=False)  # UUID of the contact
    action_type = Column(String(50), nullable=False)
    timestamp = Column(DateTime, server_default=func.now(), nullable=False)
    before_data = Column(Text, nullable=True)  # JSON string
    after_data = Column(Text, nullable=True)  # JSON string
    description = Column(String(500), nullable=True)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)

    user = relationship('User', back_populates='contact_histories')

    def __repr__(self):
        """
        Return a string representation of the ContactHistory object.

        Returns:
            str: A string representation of the ContactHistory object.
        """
        return f'<ContactHistory {self.id}: {self.action_type} on {self.contact_id}>'

    def to_dict(self):
        """
        Convert the ContactHistory object to a dictionary.

        Returns:
            dict: A dictionary representation of the ContactHistory object.
        """
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

