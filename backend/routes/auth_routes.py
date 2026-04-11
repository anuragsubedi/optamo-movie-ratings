"""
Authentication route blueprint.

Provides the login endpoint for obtaining JWT tokens.
"""

from flask import Blueprint, jsonify, request

from services.auth_service import authenticate

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/login", methods=["POST"])
def login():
    """Authenticate with username/password and receive a JWT token.

    Request body:
        {
            "username": "admin",
            "password": "password"
        }

    Returns:
        200: { "token": "<jwt_string>" }
        400: { "error": "Username and password are required" }
        401: { "error": "Invalid credentials" }
    """
    data = request.get_json()

    if not data or not data.get("username") or not data.get("password"):
        return jsonify({"error": "Username and password are required"}), 400

    token = authenticate(data["username"], data["password"])

    if not token:
        return jsonify({"error": "Invalid credentials"}), 401

    return jsonify({"token": token}), 200
