"""
Movie route blueprint.

Exposes RESTful endpoints for movie data:
  - GET /api/movies/top-rated   — High-rating-activity movies
  - GET /api/movies/details     — Single movie detail by name
  - GET /api/movies/search      — Multi-parameter search/filter
"""

from flask import Blueprint, jsonify, request

from services.auth_service import token_required
from services.movie_service import get_movie_details, get_top_rated, search_movies

movie_bp = Blueprint("movies", __name__, url_prefix="/api/movies")

@movie_bp.route("/top-rated", methods=["GET"])
@token_required
def top_rated(current_user):
    """Return movies with >10,000 ratings AND average rating > 4.0.

    Returns:
        200: List of movie objects matching the criteria.
    """
    movies = get_top_rated()
    return jsonify(movies), 200


@movie_bp.route("/details", methods=["GET"])
@token_required
def movie_details(current_user):
    """Return detailed information for a movie by name.

    Query Parameters:
        name (required): Movie name or partial name to search for.

    Returns:
        200: Movie detail object.
        400: { "error": "Movie name query parameter is required" }
        404: { "error": "Movie not found" }
    """
    name = request.args.get("name")

    if not name:
        return jsonify({"error": "Movie name query parameter is required"}), 400

    movie = get_movie_details(name)

    if not movie:
        return jsonify({"error": f"Movie not found: {name}"}), 404

    return jsonify(movie), 200


@movie_bp.route("/search", methods=["GET"])
@token_required
def search(current_user):
    """Search and filter movies by multiple optional parameters.

    Query Parameters (all optional):
        name:   Partial movie name (case-insensitive).
        genre:  Genre filter (e.g., "Drama", "Comedy").
        year:   Exact release year (integer).
        rating: Minimum average rating threshold (float).

    Returns:
        200: List of matching movie objects (max 100 results).
    """
    name = request.args.get("name")
    genre = request.args.get("genre")
    year = request.args.get("year", type=int)
    min_rating = request.args.get("rating", type=float)

    movies = search_movies(
        name=name,
        genre=genre,
        year=year,
        min_rating=min_rating,
    )
    return jsonify(movies), 200
