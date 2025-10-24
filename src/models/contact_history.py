from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base


class ContactHistory(Base):
    __tablename__ = "contact_history"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    contact_id = Column(String, nullable=False)  # UUID of the contact
    action_type = Column(String(50), nullable=False)
    timestamp = Column(DateTime, server_default=func.now(), nullable=False)
    before_data = Column(Text, nullable=True)  # JSON string
    after_data = Column(Text, nullable=True)  # JSON string
    description = Column(String(500), nullable=True)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)

    user = relationship("User", back_populates="contact_histories")

    def __repr__(self):
        return f"<ContactHistory {self.id}: {self.action_type} on {self.contact_id}>"

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "contact_id": self.contact_id,
            "action_type": self.action_type,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "description": self.description,
            "before_data": self.before_data,
            "after_data": self.after_data,
        }
