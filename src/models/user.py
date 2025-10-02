from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    oauth_provider = db.Column(db.String(50), nullable=True)  # 'google', 'apple', or None
    oauth_id = db.Column(db.String(255), nullable=True)

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
