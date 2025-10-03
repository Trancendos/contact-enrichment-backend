from functools import wraps
from flask import request, jsonify, g, current_app
from src.models.user import User

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return jsonify({"success": False, "error": "Authorization header missing"}), 401

        try:
            token = auth_header.split(" ")[1]
            
            # Ensure g.db is available from the before_request hook
            if not hasattr(g, 'db') or g.db is None:
                return jsonify({"success": False, "error": "Database session not available"}), 500

            # In a real application, you would validate the token (e.g., JWT)
            # For this example, we'll assume the token is the user's email for simplicity
            # and fetch the user from the database.
            user = g.db.query(User).filter_by(email=token).first()
            if not user:
                return jsonify({"success": False, "error": "Invalid token or user not found"}), 401
            
            g.user_id = user.id
            g.user_email = user.email

        except Exception as e:
            current_app.logger.error(f"Authentication error: {e}")
            return jsonify({"success": False, "error": f"Authentication error: {str(e)}"}), 401
        return f(*args, **kwargs)
    return decorated_function

