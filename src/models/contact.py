from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.sqlite import JSON
from .base import Base

class Contact(Base):
    """Represents a contact in the database."""
    __tablename__ = 'contacts'

    id: str = Column(String, primary_key=True, index=True)  # The unique identifier for the contact.
    user_id: int = Column(Integer, ForeignKey('users.id'), nullable=False)  # The ID of the user who owns this contact.
    full_name: str = Column(String, index=True)  # The full name of the contact.
    first_name: str = Column(String, nullable=True)  # The first name of the contact.
    last_name: str = Column(String, nullable=True)  # The last name of the contact.
    organization: str = Column(String, nullable=True)  # The organization the contact belongs to.
    title: str = Column(String, nullable=True)  # The contact's title at their organization.
    emails: list = Column(JSON, nullable=True)  # A list of email addresses for the contact.
    phones: list = Column(JSON, nullable=True)  # A list of phone numbers for the contact.
    notes: str = Column(Text, nullable=True)  # Any notes about the contact.
    tags: list = Column(JSON, nullable=True)  # A list of tags for categorizing the contact.
    related_names: list = Column(JSON, nullable=True)  # A list of names related to this contact.
    explorium_data: dict = Column(JSON, nullable=True)  # Enriched data from the Explorium service.
    created_at: DateTime = Column(DateTime, server_default=func.now())  # The timestamp when the contact was created.
    updated_at: DateTime = Column(DateTime, onupdate=func.now())  # The timestamp when the contact was last updated.

    user = relationship('User', back_populates='contacts')

    def __repr__(self):
        return f"<Contact(id='{self.id}', full_name='{self.full_name}')>"

    def to_dict(self):
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

