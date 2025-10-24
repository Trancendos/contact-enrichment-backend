"""
Base module for SQLAlchemy models.

This module provides the declarative base class for all SQLAlchemy models in
the application.
"""
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
