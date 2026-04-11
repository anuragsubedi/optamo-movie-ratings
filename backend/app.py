"""
Flask application entry point.

Creates and configures the Flask app. Registers route blueprints, initializes the database connection, and
configures CORS for the Angular frontend.

"""

import os
import sys

from flask import Flask
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint

from config import Config
from models import db
from routes.auth_routes import auth_bp
from routes.movie_routes import movie_bp

SWAGGER_URL = "/apidocs"
API_SPEC_URL = "/static/swagger.json"


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    CORS(app, origins=app.config["CORS_ORIGINS"])

    # Register route blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(movie_bp)

    # Swagger UI — served at /apidocs, spec loaded from /static/swagger.json
    swagger_bp = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_SPEC_URL,
        config={"app_name": "Movie Ratings Explorer API"},
    )
    app.register_blueprint(swagger_bp)

    # Health check endpoint
    @app.route("/api/health", methods=["GET"])
    def health():
        return {"status": "ok", "database": os.path.exists(Config.DB_PATH)}

    # Verify database exists on startup
    if not os.path.exists(Config.DB_PATH):
        print(
            f"\n!! Database not found at: {Config.DB_PATH}"
            f"\n   Run the migration first: python migrate.py\n",
            file=sys.stderr,
        )

    return app


if __name__ == "__main__":
    app = create_app()
    print(f"\n Optamo Movie Ratings API")
    print(f"   Database: {Config.DB_PATH}")
    print(f"   CORS: {Config.CORS_ORIGINS}")
    print(f"   Running on: http://localhost:5001\n")
    app.run(debug=True, port=5001)
