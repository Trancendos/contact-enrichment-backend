from flask import Blueprint, jsonify, request, g
from src.models.user import User

user_bp = Blueprint("user", __name__)

@user_bp.route("/users", methods=["GET"])
def get_users():
    users = g.db.query(User).all()
    return jsonify([user.to_dict() for user in users])

@user_bp.route("/users", methods=["POST"])
def create_user():
    data = request.json
    user = User(username=data["username"], email=data["email"], password=data["password"], name=data["name"])
    g.db.add(user)
    g.db.commit()
    g.db.refresh(user)
    return jsonify(user.to_dict()), 201

@user_bp.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = g.db.query(User).filter(User.id == user_id).first()
    if user is None:
        return jsonify({'error': 'User not found'}), 404
    return jsonify(user.to_dict())

@user_bp.route("/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    user = g.db.query(User).filter(User.id == user_id).first()
    if user is None:
        return jsonify({'error': 'User not found'}), 404
    data = request.json

    if 'username' in data and data['username'] != user.username:
        if g.db.query(User).filter(User.username == data['username']).first():
            return jsonify({'error': 'Username already taken'}), 409

    if 'email' in data and data['email'] != user.email:
        if g.db.query(User).filter(User.email == data['email']).first():
            return jsonify({'error': 'Email already taken'}), 409

    user.username = data.get("username", user.username)
    user.email = data.get("email", user.email)
    user.name = data.get("name", user.name)
    g.db.commit()
    g.db.refresh(user)
    return jsonify(user.to_dict())

@user_bp.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    user = g.db.query(User).filter(User.id == user_id).first()
    if user is None:
        return jsonify({'error': 'User not found'}), 404
    g.db.delete(user)
    g.db.commit()
    return "", 204

