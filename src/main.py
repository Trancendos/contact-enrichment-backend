import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask_session import Session # Import Flask-Session

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

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), \'static\'))
app.config[\'SECRET_KEY\'] = \'asdf#FGSgvasgf$5$WGT\'

# Configure Flask-Session
app.config[\'SESSION_TYPE\'] = \'filesystem\'
app.config[\'SESSION_PERMANENT\'] = False
app.config[\'SESSION_USE_SIGNER\'] = True
app.config[\'SESSION_FILE_DIR\'] = os.path.join(os.path.dirname(__file__), \'flask_session_data\')
Session(app) # Initialize Flask-Session

CORS(app, supports_credentials=True) # Enable CORS for all routes with credentials

# Database setup
DATABASE_URL = f"sqlite:///{os.path.join(os.path.dirname(__file__), \'database\', \'app.db\')}"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)

# Dependency to get DB session
def get_db():
    db_session = SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()

@app.before_request
def before_request():
    g.db = SessionLocal()

@app.after_request
def after_request(response):
    if hasattr(g, \'db\'):
        g.db.close()
    return response

app.register_blueprint(user_bp, url_prefix=\'/api\')
app.register_blueprint(enrichment_bp, url_prefix=\'/api\')
app.register_blueprint(auth_bp, url_prefix=\'/api/auth\')
app.register_blueprint(suggestions_bp, url_prefix=\'/api/suggestions\')
app.register_blueprint(tagging_bp)
app.register_blueprint(history_bp)
app.register_blueprint(contact_management_bp, url_prefix="/api")
app.register_blueprint(relationship_bp, url_prefix="/api")

@app.route(\'/\', defaults={\'path\': \'\'})
