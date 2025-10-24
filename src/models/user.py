from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from .base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=True)
    email = Column(String(120), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    name = Column(String(120), nullable=False)
    oauth_provider = Column(String(50), nullable=True)  # 'google', 'apple', or None
    oauth_id = Column(String(255), nullable=True)

    contacts = relationship("Contact", back_populates="user", lazy=True)
    contact_histories = relationship("ContactHistory", back_populates="user", lazy=True)
    contact_relationships = relationship(
        "ContactRelationship", back_populates="user", lazy=True
    )

    def __repr__(self):
        return f"<User {self.email}>"

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "name": self.name,
            "oauth_provider": self.oauth_provider,
        }
