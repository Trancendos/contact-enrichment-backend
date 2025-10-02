from src.models.user import db
from datetime import datetime

class Suggestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    contact_id = db.Column(db.String(255), nullable=False)  # Frontend contact ID
    field_name = db.Column(db.String(100), nullable=False)  # e.g., 'email', 'phone', 'name'
    current_value = db.Column(db.String(500), nullable=True)
    suggested_value = db.Column(db.String(500), nullable=False)
    confidence = db.Column(db.Float, nullable=False)  # 0.0 to 1.0
    source = db.Column(db.String(255), nullable=False)  # e.g., 'LinkedIn', 'Twitter', 'Web Search'
    status = db.Column(db.String(50), default='pending')  # 'pending', 'approved', 'rejected'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Suggestion {self.id} for contact {self.contact_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'contact_id': self.contact_id,
            'field_name': self.field_name,
            'current_value': self.current_value,
            'suggested_value': self.suggested_value,
            'confidence': self.confidence,
            'source': self.source,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
