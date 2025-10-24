from functools import wraps
from flask import request, jsonify, g, current_app, session
from src.models.user import User

def login_required(f):
    """Decorator to protect routes that require authentication.

    This decorator checks for a valid user ID in the session, verifies
    that the user exists in the database, and then stores the user's ID
    and email in the Flask global object `g` for the duration of the
    request.

    Args:
        f: The function to decorate.

    Returns:
        The decorated function.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("user_id"):
            return jsonify({"success": False, "error": "Unauthorized"}), 401

        try:
            if not hasattr(g, 'db') or g.db is None:
                return jsonify({"success": False, "error": "Database session not available"}), 500

            user = g.db.query(User).filter_by(id=session["user_id"]).first()
            if not user:
                return jsonify({"success": False, "error": "User not found"}), 401
            
            g.user_id = user.id
            g.user_email = user.email

        except Exception as e:
            current_app.logger.error(f"Authentication error: {e}")
            return jsonify({"success": False, "error": f"Authentication error: {str(e)}"}), 401
        return f(*args, **kwargs)
    return decorated_function

