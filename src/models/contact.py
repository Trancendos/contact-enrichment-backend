from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.sqlite import JSON
from .base import Base


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(String, primary_key=True, index=True)  # UUID as string
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
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

    user = relationship("User", back_populates="contacts")

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
