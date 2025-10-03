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
    user = g.db.query(User).filter(User.id == user_id).first_or_404()
    return jsonify(user.to_dict())

@user_bp.route("/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    user = g.db.query(User).filter(User.id == user_id).first_or_404()
    data = request.json
    user.username = data.get("username", user.username)
    user.email = data.get("email", user.email)
    user.name = data.get("name", user.name)
    g.db.commit()
    g.db.refresh(user)
    return jsonify(user.to_dict())

@user_bp.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    user = g.db.query(User).filter(User.id == user_id).first_or_404()
    g.db.delete(user)
    g.db.commit()
    return "", 204

