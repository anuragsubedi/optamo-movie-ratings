"""
Application configuration - centralizes all configuration values (database URI, JWT secret, CORS origins)
with environment-variable overrides.

Note: 
The environment values are hardcoded here for simplicity. 
We can use an explicit ".env" file to store these values and load them as well.
"""

import os

class Config:

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    # SQLite database
    DB_PATH = os.path.join(BASE_DIR, "movie_ratings.db")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{DB_PATH}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT authentication
    JWT_SECRET_KEY = os.environ.get(
        "JWT_SECRET_KEY", "optamo-dev-secret-key-change-in-production-32b"
    )
    JWT_EXPIRATION_HOURS = 1

    # CORS — allow Angular dev server
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "http://localhost:4200")

    # CSV data directory (used by migration script only)
    CSV_DATA_DIR = os.environ.get(
        "CSV_DATA_DIR",
        os.path.join(BASE_DIR, "..", "movie_ratings"),
    )
