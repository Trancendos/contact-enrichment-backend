from functools import wraps
from flask import session, jsonify, g

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get("user_id")
        if user_id is None:
            return jsonify({"error": "Unauthorized: Login required"}), 401
        g.user_id = user_id
        return f(*args, **kwargs)
    return decorated_function

