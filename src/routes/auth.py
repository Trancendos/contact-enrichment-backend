from flask import Blueprint, request, jsonify, session, g
from werkzeug.security import generate_password_hash, check_password_hash
from src.models.user import User
import secrets

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    """Registers a new user.

    Retrieves user registration data (email, password, name) from the
    request JSON, creates a new user, and logs them in by creating a
    session.

    Returns:
        A JSON response indicating success or failure. On success,
        includes the new user's information.
    """
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    name = data.get("name")

    print(f"Received registration data: {data}")
    if not email or not password or not name:
        print("Missing email, password, or name")
        return jsonify({"error": "Email, password, and name are required"}), 400

    # Check if user already exists
    existing_user = g.db.query(User).filter_by(email=email).first()
    if existing_user:
        return jsonify({"error": "User with this email already exists"}), 400

    # Create new user
    hashed_password = generate_password_hash(password)
    new_user = User(email=email, password=hashed_password, name=name)
    
    g.db.add(new_user)
    g.db.commit()
    g.db.refresh(new_user)

    # Automatically log in the user
    session["user_id"] = new_user.id
    session["user_email"] = new_user.email
    session["user_name"] = new_user.name

    return jsonify({
        "success": True, 
        "message": "User registered successfully",
        "user": {
            "id": new_user.id,
            "email": new_user.email,
            "name": new_user.name
        }
    })

@auth_bp.route("/login", methods=["POST"])
def login():
    """Logs in an existing user.

    Retrieves user credentials (email, password) from the request JSON,
    verifies them, and creates a session upon successful authentication.

    Returns:
        A JSON response indicating success or failure. On success,
        includes the user's information.
    """
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    user = g.db.query(User).filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        return jsonify({"error": "Invalid email or password"}), 401

    # Create session
    session["user_id"] = user.id
    session["user_email"] = user.email
    session["user_name"] = user.name

    return jsonify({
        "success": True, 
        "message": "Login successful",
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name
        }
    })

@auth_bp.route("/logout", methods=["POST"])
def logout():
    """Logs out the current user.

    Clears the session, effectively logging the user out.

    Returns:
        A JSON response indicating successful logout.
    """
    session.clear()
    return jsonify({"success": True, "message": "Logged out successfully"})

@auth_bp.route("/me", methods=["GET"])
def get_current_user():
    """Retrieves the currently authenticated user's information.

    Fetches the current user's data from the database based on the
    session user ID.

    Returns:
        A JSON response with the user's information if authenticated,
        otherwise an error message.
    """
    user_id = session.get("user_id")
    
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401

    user = g.db.query(User).filter(User.id == user_id).first()
    
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "success": True,
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name
        }
    })

@auth_bp.route("/oauth/google", methods=["POST"])
def google_oauth():
    """Placeholder for Google OAuth implementation.

    This endpoint is a mock for Google OAuth. In a production
    environment, it would verify the provided Google token, and then
    either create a new user or log in an existing one.

    Returns:
        A JSON response indicating the feature is not yet implemented.
    """
    # Placeholder for Google OAuth implementation
    # In production, this would verify the Google token and create/login user
    data = request.get_json()
    google_token = data.get("token")
    
    # Mock implementation - in production, verify token with Google
    return jsonify({
        "success": True,
        "message": "Google OAuth not yet implemented. Use email/password login.",
        "note": "This requires Google OAuth client ID and secret configuration"
    })

@auth_bp.route("/oauth/apple", methods=["POST"])
def apple_oauth():
    """Placeholder for Apple Sign-In implementation.

    This endpoint is a mock for Apple Sign-In. In a production
    environment, it would verify the provided Apple token, and then
    either create a new user or log in an existing one.

    Returns:
        A JSON response indicating the feature is not yet implemented.
    """
    # Placeholder for Apple Sign-In implementation
    # In production, this would verify the Apple token and create/login user
    data = request.get_json()
    apple_token = data.get("token")
    
    # Mock implementation - in production, verify token with Apple
    return jsonify({
        "success": True,
        "message": "Apple Sign-In not yet implemented. Use email/password login.",
        "note": "This requires Apple Sign-In configuration"
    })

