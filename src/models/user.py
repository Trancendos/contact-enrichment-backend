from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from .base import Base

class User(Base):
    """Represents a user of the application."""
    __tablename__ = 'users'

    id: int = Column(Integer, primary_key=True)  # The unique identifier for the user.
    username: str = Column(String(80), unique=True, nullable=True)  # The user's username.
    email: str = Column(String(120), unique=True, nullable=False)  # The user's email address.
    password: str = Column(String(255), nullable=False)  # The user's hashed password.
    name: str = Column(String(120), nullable=False)  # The user's full name.
    oauth_provider: str = Column(String(50), nullable=True)  # The OAuth provider used for authentication.
    oauth_id: str = Column(String(255), nullable=True)  # The user's ID from the OAuth provider.

    contacts = relationship('Contact', back_populates='user', lazy=True)
    contact_histories = relationship('ContactHistory', back_populates='user', lazy=True)
    contact_relationships = relationship('ContactRelationship', back_populates='user', lazy=True)

    def __repr__(self):
        return f'<User {self.email}>'

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'name': self.name,
            'oauth_provider': self.oauth_provider
        }

