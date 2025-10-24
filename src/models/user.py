"""
SQLAlchemy model for a user.
"""
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from .base import Base


class User(Base):
    """
    Represents a user in the database.

    Attributes:
        id (int): The unique identifier for the user.
        username (str): The username of the user.
        email (str): The email address of the user.
        password (str): The hashed password of the user.
        name (str): The name of the user.
        oauth_provider (str): The OAuth provider used for authentication (e.g., 'google', 'apple').
        oauth_id (str): The user's ID from the OAuth provider.
        contacts (list): A list of contacts associated with the user.
        contact_histories (list): A list of contact histories associated with the user.
        contact_relationships (list): A list of contact relationships associated with the user.
    """
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=True)
    email = Column(String(120), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    name = Column(String(120), nullable=False)
    oauth_provider = Column(String(50), nullable=True)  # 'google', 'apple', or None
    oauth_id = Column(String(255), nullable=True)

    contacts = relationship('Contact', back_populates='user', lazy=True)
    contact_histories = relationship('ContactHistory', back_populates='user', lazy=True)
    contact_relationships = relationship('ContactRelationship', back_populates='user', lazy=True)

    def __repr__(self):
        """
        Return a string representation of the User object.

        Returns:
            str: A string representation of the User object.
        """
        return f'<User {self.email}>'

    def to_dict(self):
        """
        Convert the User object to a dictionary.

        Returns:
            dict: A dictionary representation of the User object.
        """
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'name': self.name,
            'oauth_provider': self.oauth_provider
        }

