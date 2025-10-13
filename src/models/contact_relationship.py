from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.models.base import Base

class ContactRelationship(Base):
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
        return f"<ContactRelationship(id={self.id}, contact_id_1='{self.contact_id_1}', contact_id_2='{self.contact_id_2}', type='{self.relationship_type}')>"

