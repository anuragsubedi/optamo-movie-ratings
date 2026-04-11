"""
Authentication service.

Provides JWT token generation, validation, and a route-protection decorator.
This is just a minimal proof-of-concept for authentication.

Demo credentials: admin / password
"""

import datetime
import functools

import jwt
from flask import current_app, jsonify, request

# Hardcoded demo credentials — in production, this would be a database lookup
# with bcrypt-hashed passwords.
DEMO_USERS = {
    "admin": "password",
}

def authenticate(username: str, password: str) -> str | None:
    """Validate credentials and return a signed JWT if valid.

    Args:
        username: The username to authenticate.
        password: The plaintext password to verify.

    Returns:
        A signed JWT string, or None if credentials are invalid.
    """
    if DEMO_USERS.get(username) != password:
        return None

    payload = {
        "sub": username,
        "iat": datetime.datetime.now(datetime.timezone.utc),
        "exp": datetime.datetime.now(datetime.timezone.utc)
        + datetime.timedelta(hours=current_app.config["JWT_EXPIRATION_HOURS"]),
    }
    token = jwt.encode(payload, current_app.config["JWT_SECRET_KEY"], algorithm="HS256")
    return token


def token_required(f):
    """Decorator that protects a route with JWT authentication.

    Expects the request to include an 'Authorization: Bearer <token>' header.
    Passes the decoded token payload as the first argument to the wrapped
    function.
    """

    @functools.wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")

        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid Authorization header"}), 401

        token = auth_header.split(" ", 1)[1]

        try:
            payload = jwt.decode(
                token, current_app.config["JWT_SECRET_KEY"], algorithms=["HS256"]
            )
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        return f(payload, *args, **kwargs)

    return decorated
