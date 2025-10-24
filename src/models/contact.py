"""
SQLAlchemy model for a contact.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.sqlite import JSON
from .base import Base


class Contact(Base):
    """
    Represents a contact in the database.

    Attributes:
        id (str): The unique identifier for the contact (UUID).
        user_id (int): The ID of the user who owns this contact.
        full_name (str): The full name of the contact.
        first_name (str): The first name of the contact.
        last_name (str): The last name of the contact.
        organization (str): The organization the contact belongs to.
        title (str): The job title of the contact.
        emails (list): A list of email addresses associated with the contact.
        phones (list): A list of phone numbers associated with the contact.
        notes (str): Any notes about the contact.
        tags (list): A list of tags associated with the contact.
        related_names (list): A list of related names for merged contacts.
        explorium_data (dict): Enriched data from the Explorium service.
        created_at (datetime): The timestamp when the contact was created.
        updated_at (datetime): The timestamp when the contact was last updated.
        user (User): The user who owns this contact.
    """
    __tablename__ = 'contacts'

    id = Column(String, primary_key=True, index=True)  # UUID as string
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    full_name = Column(String, index=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    organization = Column(String, nullable=True)
    title = Column(String, nullable=True)
    emails = Column(JSON, nullable=True)  # List of dicts: [{value: "", type: ""}]
    phones = Column(JSON, nullable=True)  # List of dicts: [{value: "", type: ""}]
    notes = Column(Text, nullable=True)
    tags = Column(JSON, nullable=True)  # List of strings
    related_names = Column(JSON, nullable=True)  # For merged contacts
    explorium_data = Column(JSON, nullable=True)  # Enriched data from Explorium
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    user = relationship('User', back_populates='contacts')

    def __repr__(self):
        """
        Return a string representation of the Contact object.

        Returns:
            str: A string representation of the Contact object.
        """
        return f"<Contact(id='{self.id}', full_name='{self.full_name}')>"

    def to_dict(self):
        """
        Convert the Contact object to a dictionary.

        Returns:
            dict: A dictionary representation of the Contact object.
        """
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
            "related_names": self.related_names,
            "explorium_data": self.explorium_data,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

