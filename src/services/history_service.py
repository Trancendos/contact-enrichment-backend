import json
from datetime import datetime
from src.models.contact_history import ContactHistory
from src.models.user import db

class HistoryService:
    """Service for logging contact changes and managing history"""
    
    @staticmethod
    def log_action(user_id, contact_id, action_type, before_data=None, after_data=None, description=None, request=None):
        """
        Log a contact action to the history database.
        
        Args:
            user_id: ID of the user performing the action
            contact_id: ID of the contact being modified
            action_type: Type of action ('create', 'update', 'delete', 'split', 'merge')
            before_data: Contact data before the change (dict)
            after_data: Contact data after the change (dict)
            description: Human-readable description of the change
            request: Flask request object for extracting IP and user agent
            
        Returns:
            ContactHistory object
        """
        try:
            history_entry = ContactHistory(
                user_id=user_id,
                contact_id=contact_id,
                action_type=action_type,
                before_data=json.dumps(before_data) if before_data else None,
                after_data=json.dumps(after_data) if after_data else None,
                description=description or f"{action_type.capitalize()} contact",
                ip_address=request.remote_addr if request else None,
                user_agent=request.headers.get('User-Agent') if request else None
            )
            
            db.session.add(history_entry)
            db.session.commit()
            
            return history_entry
        except Exception as e:
            print(f"Error logging history: {e}")
            db.session.rollback()
            return None
    
    @staticmethod
    def get_contact_history(user_id, contact_id, limit=50):
        """
        Get history for a specific contact.
        
        Args:
            user_id: ID of the user
            contact_id: ID of the contact
            limit: Maximum number of history entries to return
            
        Returns:
            List of ContactHistory objects
        """
        try:
            history = ContactHistory.query.filter_by(
                user_id=user_id,
                contact_id=contact_id
            ).order_by(ContactHistory.timestamp.desc()).limit(limit).all()
            
            return [h.to_dict() for h in history]
        except Exception as e:
            print(f"Error getting contact history: {e}")
            return []
    
    @staticmethod
    def get_user_history(user_id, limit=100):
        """
        Get all history for a user.
        
        Args:
            user_id: ID of the user
            limit: Maximum number of history entries to return
            
        Returns:
            List of ContactHistory objects
        """
        try:
            history = ContactHistory.query.filter_by(
                user_id=user_id
            ).order_by(ContactHistory.timestamp.desc()).limit(limit).all()
            
            return [h.to_dict() for h in history]
        except Exception as e:
            print(f"Error getting user history: {e}")
            return []
    
    @staticmethod
    def get_recent_actions(user_id, action_types=None, limit=20):
        """
        Get recent actions for a user, optionally filtered by action type.
        
        Args:
            user_id: ID of the user
            action_types: List of action types to filter by (optional)
            limit: Maximum number of history entries to return
            
        Returns:
            List of ContactHistory objects
        """
        try:
            query = ContactHistory.query.filter_by(user_id=user_id)
            
            if action_types:
                query = query.filter(ContactHistory.action_type.in_(action_types))
            
            history = query.order_by(ContactHistory.timestamp.desc()).limit(limit).all()
            
            return [h.to_dict() for h in history]
        except Exception as e:
            print(f"Error getting recent actions: {e}")
            return []
    
    @staticmethod
    def undo_action(user_id, history_id):
        """
        Undo a specific action by restoring the before_data.
        
        Args:
            user_id: ID of the user
            history_id: ID of the history entry to undo
            
        Returns:
            Dict with success status and restored contact data
        """
        try:
            history_entry = ContactHistory.query.filter_by(
                id=history_id,
                user_id=user_id
            ).first()
            
            if not history_entry:
                return {'success': False, 'error': 'History entry not found'}
            
            if not history_entry.before_data:
                return {'success': False, 'error': 'No before data available for undo'}
            
            # Parse the before data
            before_data = json.loads(history_entry.before_data)
            
            # Log the undo action
            HistoryService.log_action(
                user_id=user_id,
                contact_id=history_entry.contact_id,
                action_type='undo',
                before_data=json.loads(history_entry.after_data) if history_entry.after_data else None,
                after_data=before_data,
                description=f"Undo {history_entry.action_type}"
            )
            
            return {
                'success': True,
                'contact_data': before_data,
                'original_action': history_entry.action_type
            }
        except Exception as e:
            print(f"Error undoing action: {e}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def create_backup(user_id, contacts_data):
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
                contact_id='BACKUP',
                action_type='backup',
                after_data=json.dumps(contacts_data),
                description=f"Backup of {len(contacts_data)} contacts"
            )
            
            db.session.add(backup_entry)
            db.session.commit()
            
            return backup_entry.to_dict()
        except Exception as e:
            print(f"Error creating backup: {e}")
            db.session.rollback()
            return None
    
    @staticmethod
    def get_backups(user_id, limit=10):
        """
        Get all backups for a user.
        
        Args:
            user_id: ID of the user
            limit: Maximum number of backups to return
            
        Returns:
            List of backup history entries
        """
        try:
            backups = ContactHistory.query.filter_by(
                user_id=user_id,
                contact_id='BACKUP',
                action_type='backup'
            ).order_by(ContactHistory.timestamp.desc()).limit(limit).all()
            
            return [b.to_dict() for b in backups]
        except Exception as e:
            print(f"Error getting backups: {e}")
            return []
