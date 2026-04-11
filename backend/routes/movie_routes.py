"""
Movie route blueprint.

Exposes RESTful endpoints for movie data:
  - GET /api/movies/top-rated   — Paginated high-rating-activity movies
  - GET /api/movies/details     — Single movie detail by name
  - GET /api/movies/search      — Paginated, multi-parameter search/filter

All list endpoints accept the following pagination and sorting parameters:
  page      (int,   default 1)    — 1-indexed page number
  per_page  (int,   default 25)   — rows per page, clamped server-side to 1–100
  sort_by   (str)                 — one of: name, release_year, average_rating,
                                    number_user_rated
  sort_dir  (str,   'asc'|'desc') — sort direction

Responses from list endpoints are paginated envelopes:
  {
      "data":     [ ...Movie objects... ],
      "total":    int,   # total matching rows (ignoring pagination)
      "page":     int,
      "per_page": int,
      "pages":    int    # total number of available pages
  }
"""

from flask import Blueprint, jsonify, request

from services.auth_service import token_required
from services.movie_service import get_movie_details, get_top_rated, search_movies

movie_bp = Blueprint("movies", __name__, url_prefix="/api/movies")

# Valid sort column keys — used to sanitise sort_by before passing to service.
_VALID_SORT_COLUMNS = {"name", "release_year", "average_rating", "number_user_rated"}


def _parse_page_params(
    default_sort_by: str = "name",
    default_sort_dir: str = "asc",
) -> tuple[int, int, str, str]:
    """Extract and sanitize pagination / sorting query parameters.

    Returns:
        (page, per_page, sort_by, sort_dir) — all guaranteed to be safe values.
    """
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=25, type=int)
    sort_by = request.args.get("sort_by", default=default_sort_by)
    sort_dir = request.args.get("sort_dir", default=default_sort_dir)

    # Clamp numeric params to sensible bounds
    page = max(page, 1)
    per_page = min(max(per_page, 1), 100)

    # Sanitise string params — fall back to defaults if values are unknown
    if sort_by not in _VALID_SORT_COLUMNS:
        sort_by = default_sort_by
    if sort_dir not in ("asc", "desc"):
        sort_dir = default_sort_dir

    return page, per_page, sort_by, sort_dir


@movie_bp.route("/top-rated", methods=["GET"])
@token_required
def top_rated(current_user):
    """Return paginated movies with >10,000 ratings AND average rating > 4.0.

    Query Parameters:
        page     (int,   default 1)              — Page number (1-indexed).
        per_page (int,   default 25, max 100)    — Results per page.
        sort_by  (str,   default average_rating) — Column to sort on.
        sort_dir (str,   default desc)           — 'asc' or 'desc'.

    Returns:
        200: Paginated envelope {data, total, page, per_page, pages}.
    """
    page, per_page, sort_by, sort_dir = _parse_page_params(
        default_sort_by="average_rating", default_sort_dir="desc"
    )
    result = get_top_rated(
        page=page, per_page=per_page, sort_by=sort_by, sort_dir=sort_dir
    )
    return jsonify(result), 200


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

    Query Parameters (all optional unless noted):
        name     (str):   Partial movie name (case-insensitive).
        genre    (str):   Genre filter (e.g., "Drama", "Comedy").
        year     (int):   Exact release year.
        rating   (float): Minimum average rating threshold.
        page     (int,   default 1)    — Page number (1-indexed).
        per_page (int,   default 25)   — Results per page (max 100).
        sort_by  (str,   default name) — Column to sort on.
        sort_dir (str,   default asc)  — 'asc' or 'desc'.

    Returns:
        200: Paginated envelope {data, total, page, per_page, pages}.
    """
    name = request.args.get("name")
    genre = request.args.get("genre")
    year = request.args.get("year", type=int)
    min_rating = request.args.get("rating", type=float)

    page, per_page, sort_by, sort_dir = _parse_page_params(
        default_sort_by="name", default_sort_dir="asc"
    )

    result = search_movies(
        name=name,
        genre=genre,
        year=year,
        min_rating=min_rating,
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )
    return jsonify(result), 200
