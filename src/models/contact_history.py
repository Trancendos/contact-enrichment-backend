from datetime import datetime
from src.models.user import db

class ContactHistory(db.Model):
    """Model for tracking contact change history"""
    __tablename__ = 'contact_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    contact_id = db.Column(db.String(100), nullable=False)  # UUID of the contact
    action_type = db.Column(db.String(50), nullable=False)  # 'create', 'update', 'delete', 'split', 'merge'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Store the contact data before the change (for undo functionality)
    before_data = db.Column(db.Text)  # JSON string
    
    # Store the contact data after the change
    after_data = db.Column(db.Text)  # JSON string
    
    # Additional metadata
    description = db.Column(db.String(500))  # Human-readable description of the change
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(500))
    
    def __repr__(self):
        return f'<ContactHistory {self.id}: {self.action_type} on {self.contact_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'contact_id': self.contact_id,
            'action_type': self.action_type,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'description': self.description,
            'before_data': self.before_data,
            'after_data': self.after_data
        }
