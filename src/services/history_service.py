"""
Service for managing contact history and backups.

This service provides methods for logging contact actions, retrieving history,
undoing actions, and creating and retrieving backups.
"""
from sqlalchemy.orm import Session
import json
from datetime import datetime
from src.models.contact_history import ContactHistory


class HistoryService:
    """
    A service for managing contact history and backups.
    """

    def __init__(self, db_session: Session):
        """
        Initialize the HistoryService.

        Args:
            db_session (sqlalchemy.orm.Session): The database session.
        """
        self.db_session = db_session

    def log_action(self, user_id, contact_id, action_type, before_data=None, after_data=None, description=None, request_info=None):
        """
        Log a contact action to the history database.

        Args:
            user_id (int): The ID of the user performing the action.
            contact_id (str): The ID of the contact being modified.
            action_type (str): The type of action (e.g., "create", "update").
            before_data (dict, optional): The contact data before the change.
                Defaults to None.
            after_data (dict, optional): The contact data after the change.
                Defaults to None.
            description (str, optional): A human-readable description of the
                change. Defaults to None.
            request_info (dict, optional): Information about the request
                that triggered the action. Defaults to None.

        Returns:
            ContactHistory: The newly created ContactHistory object, or None
                if an error occurred.
        """
        try:
            history_entry = ContactHistory(
                user_id=user_id,
                contact_id=contact_id,
                action_type=action_type,
                before_data=json.dumps(before_data, default=str) if before_data else None,
                after_data=json.dumps(after_data, default=str) if after_data else None,
                description=description or f"{action_type.capitalize()} contact",
                ip_address=request_info.get("ip_address") if request_info else None,
                user_agent=request_info.get("user_agent") if request_info else None
            )
            
            self.db_session.add(history_entry)
            self.db_session.commit()
            
            return history_entry
        except Exception as e:
            print(f"Error logging history: {e}")
            self.db_session.rollback()
            return None
    
    def get_contact_history(self, user_id, contact_id, limit=50):
        """
        Get the history for a specific contact.

        Args:
            user_id (int): The ID of the user.
            contact_id (str): The ID of the contact.
            limit (int, optional): The maximum number of history entries to
                return. Defaults to 50.

        Returns:
            list: A list of contact history dictionaries.
        """
        try:
            history = self.db_session.query(ContactHistory).filter_by(
                user_id=user_id,
                contact_id=contact_id
            ).order_by(ContactHistory.timestamp.desc()).limit(limit).all()
            
            return [h.to_dict() for h in history]
        except Exception as e:
            print(f"Error getting contact history: {e}")
            return []
    
    def get_user_history(self, user_id, limit=100):
        """
        Get all history for a user.

        Args:
            user_id (int): The ID of the user.
            limit (int, optional): The maximum number of history entries to
                return. Defaults to 100.

        Returns:
            list: A list of contact history dictionaries.
        """
        try:
            history = self.db_session.query(ContactHistory).filter_by(
                user_id=user_id
            ).order_by(ContactHistory.timestamp.desc()).limit(limit).all()
            
            return [h.to_dict() for h in history]
        except Exception as e:
            print(f"Error getting user history: {e}")
            return []
    
    def get_recent_actions(self, user_id, action_types=None, limit=20):
        """
        Get recent actions for a user, optionally filtered by action type.

        Args:
            user_id (int): The ID of the user.
            action_types (list, optional): A list of action types to filter
                by. Defaults to None.
            limit (int, optional): The maximum number of history entries to
                return. Defaults to 20.

        Returns:
            list: A list of contact history dictionaries.
        """
        try:
            query = self.db_session.query(ContactHistory).filter_by(user_id=user_id)
            
            if action_types:
                query = query.filter(ContactHistory.action_type.in_(action_types))
            
            history = query.order_by(ContactHistory.timestamp.desc()).limit(limit).all()
            
            return [h.to_dict() for h in history]
        except Exception as e:
            print(f"Error getting recent actions: {e}")
            return []
    
    def undo_action(self, user_id, history_id):
        """
        Undo a specific action by restoring the before_data.
        
        Args:
            user_id: ID of the user
            history_id: ID of the history entry to undo
            
        Returns:
            Dict with success status and restored contact data
        """
        try:
            history_entry = self.db_session.query(ContactHistory).filter_by(
                id=history_id,
                user_id=user_id
            ).first()
            
            if not history_entry:
                return {"success": False, "error": "History entry not found"}
            
            if not history_entry.before_data:
                return {"success": False, "error": "No before data available for undo"}
            
            # Parse the before data
            before_data = json.loads(history_entry.before_data)
            
            # Log the undo action
            self.log_action(
                user_id=user_id,
                contact_id=history_entry.contact_id,
                action_type="undo",
                before_data=json.loads(history_entry.after_data) if history_entry.after_data else None,
                after_data=before_data,
                description=f"Undo {history_entry.action_type}"
            )
            
            return {
                "success": True,
                "contact_data": before_data,
                "original_action": history_entry.action_type
            }
        except Exception as e:
            print(f"Error undoing action: {e}")
            return {"success": False, "error": str(e)}
    
    def create_backup(self, user_id, contacts_data):
        """
        Create a backup of all contacts.
        
        Args:
            user_id: ID of the user
            contacts_data: List of contact dictionaries
            
        Returns:
            ContactHistory object representing the backup
        """
        try:
            backup_entry = ContactHistory(
                user_id=user_id,
                contact_id="BACKUP",
                action_type="backup",
                after_data=json.dumps(contacts_data, default=str),
                description=f"Backup of {len(contacts_data)} contacts"
            )
            
            self.db_session.add(backup_entry)
            self.db_session.commit()
            
            return backup_entry.to_dict()
        except Exception as e:
            print(f"Error creating backup: {e}")
            self.db_session.rollback()
            return None
    
    def get_backups(self, user_id, limit=10):
        """
        Get all backups for a user.
        
        Args:
            user_id: ID of the user
            limit: Maximum number of backups to return
            
        Returns:
            List of backup history entries
        """
        try:
            backups = self.db_session.query(ContactHistory).filter_by(
                user_id=user_id,
                contact_id="BACKUP",
                action_type="backup"
            ).order_by(ContactHistory.timestamp.desc()).limit(limit).all()
            
            return [b.to_dict() for b in backups]
        except Exception as e:
            print(f"Error getting backups: {e}")
            return []
