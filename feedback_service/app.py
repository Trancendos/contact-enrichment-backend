
import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# --- App Setup ---
# Sets up the Flask application.
# The database is stored in the 'instance' folder, which Flask creates.
app = Flask(__name__)
# Configure the database URI for SQLite.
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///feedback.db'
# Disable the modification tracking feature of SQLAlchemy, as it's not needed
# and can consume extra memory.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# --- Database Setup ---
# Initialize the SQLAlchemy extension with the Flask app.
db = SQLAlchemy(app)

# --- Database Model ---
# Defines the structure of the 'feedback' table in the database.
class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(80), nullable=True) # User ID can be optional
    feedback_text = db.Column(db.String(500), nullable=False)
    source = db.Column(db.String(120), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        """Serializes the Feedback object to a dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'feedback_text': self.feedback_text,
            'source': self.source,
            'timestamp': self.timestamp.isoformat()
        }

# --- API Endpoints ---
@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    """Receives feedback submissions and saves them to the database."""
    data = request.get_json()

    # --- Validation ---
    if not data:
        return jsonify({'error': 'Invalid JSON payload'}), 400

    feedback_text = data.get('feedback_text')
    source = data.get('source')
    user_id = data.get('user_id') # Optional

    if not feedback_text or not source:
        return jsonify({'error': 'Missing required fields: feedback_text and source'}), 400

    # --- Database Interaction ---
    new_feedback = Feedback(
        user_id=user_id,
        feedback_text=feedback_text,
        source=source
    )
    db.session.add(new_feedback)
    db.session.commit()

    return jsonify(new_feedback.to_dict()), 201

# --- Initialization ---
# This block ensures that the database tables are created before the first request.
# A lock is used to prevent race conditions in a multi-threaded environment.
from threading import Lock
app.tables_created_lock = Lock()

@app.before_request
def create_tables():
    # The 'app_context' is necessary for Flask extensions to access the application.
    with app.tables_created_lock:
        if not hasattr(app, 'tables_created'):
            with app.app_context():
                db.create_all()
            app.tables_created = True

if __name__ == '__main__':
    # Runs the Flask application.
    # The host '0.0.0.0' makes the server publicly available.
    app.run(host='0.0.0.0', port=5001, debug=True)
