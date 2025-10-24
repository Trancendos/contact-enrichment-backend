"""
Main application file for the Flask-based Contact Enrichment Backend.

This file initializes the Flask application, configures the database connection,
registers blueprints for different API routes, and defines middleware for
managing database sessions. It also includes a catch-all route to serve the
static frontend application.
"""
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# DON\'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, session, g
from src.models.base import Base
from src.models.user import User
from src.models.contact import Contact # Assuming Contact model exists or will be created
from src.models.contact_history import ContactHistory
from src.models.contact_relationship import ContactRelationship
from src.models.suggestion import Suggestion

from src.routes.user import user_bp
from src.routes.enrichment import enrichment_bp
from src.routes.auth import auth_bp
from src.routes.suggestions import suggestions_bp
from src.routes.tagging import tagging_bp
from src.routes.history import history_bp
from src.routes.contact_management import contact_management_bp
from src.routes.relationship import relationship_bp

from flask_cors import CORS

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'asdf#FGSgvasgf$5$WGT')

CORS(app, supports_credentials=True) # Enable CORS for all routes with credentials

# Database setup
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
DATABASE_URL = f"{SUPABASE_URL}/rest/v1/?apikey={SUPABASE_KEY}"
engine = create_engine(f"postgresql://postgres:{SUPABASE_KEY}@{SUPABASE_URL.replace('https://', '').split('.')[0]}.supabase.co:5432/postgres")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
# Base.metadata.create_all(bind=engine) # Supabase handles migrations

# Dependency to get DB session
def get_db():
    """
    A generator function that provides a database session for a request.

    This function is used as a dependency in API endpoints to get a database
    session. It ensures that the session is properly closed after the request
    is finished.

    Yields:
        sqlalchemy.orm.Session: The database session.
    """
    db_session = SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()

@app.before_request
def before_request():
    """
    Middleware to create a new database session before each request.

    This function is executed before each request to the application. It creates
    a new database session and stores it in the Flask global object `g`.
    """
    g.db = SessionLocal()

@app.after_request
def after_request(response):
    """
    Middleware to close the database session after each request.

    This function is executed after each request. It checks if a database
    session exists in the Flask global object `g` and closes it if it does.

    Args:
        response (flask.Response): The response object to be sent to the client.

    Returns:
        flask.Response: The same response object.
    """
    if hasattr(g, 'db'):
        g.db.close()
    return response

app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(enrichment_bp, url_prefix='/api')
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(suggestions_bp, url_prefix='/api/suggestions')
app.register_blueprint(tagging_bp, url_prefix='/api/tagging')
app.register_blueprint(history_bp, url_prefix='/api/history')
app.register_blueprint(contact_management_bp, url_prefix='/api')
app.register_blueprint(relationship_bp, url_prefix='/api')

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    """
    Serve the static frontend application.

    This is a catch-all route that serves the static files for the frontend
    application. If a requested path exists in the static folder, it serves
    that file. Otherwise, it serves the `index.html` file, which allows the
    frontend to handle routing.

    Args:
        path (str): The path to the file to serve.

    Returns:
        flask.Response: The requested file or `index.html`.
    """
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    # Only enable debug mode if ENVIRONMENT is not production
    is_debug = os.environ.get('ENVIRONMENT', 'development') != 'production'
    app.run(host='0.0.0.0', port=5000, debug=is_debug)

