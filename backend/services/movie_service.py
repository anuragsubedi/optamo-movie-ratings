"""
Movie service — business logic layer.

Encapsulates all data access and transformation logic for movie-related
endpoints. Components (routes) call these functions instead of writing
queries directly, maintaining clean separation of concerns.

All list-returning functions now emit a paginated envelope:
    {
        "data":     [Movie, ...],
        "total":    int,     # total rows matching the filter (without LIMIT)
        "page":     int,     # current 1-indexed page
        "per_page": int,     # page size
        "pages":    int,     # total number of pages
    }

Sorting and pagination are resolved entirely in SQLite so the Python
process never loads more rows than the caller actually needs.
"""

import math

from models import Movie, MovieStats, db

# ---------------------------------------------------------------------------
# Sort-column resolution
# ---------------------------------------------------------------------------

# Maps the API-facing column key to its SQLAlchemy ORM attribute.
# Any sort_by value NOT present in this map is silently ignored and the
# caller's default_sort_col is used instead, preventing SQL injection.
_SORT_COLUMN_MAP = {
    "name": Movie.name,
    "release_year": Movie.release_year,
    "average_rating": MovieStats.average_rating,
    "number_user_rated": MovieStats.number_user_rated,
}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _serialize_movie(movie: Movie) -> dict:
    """Convert a Movie ORM object to the API response format.

    Matches the shape defined in output_sample.json:
    {
        "name": str,
        "genre": [str],
        "release_year": int | None,
        "number_user_rated": int,
        "average_rating": float
    }
    """
    genres = movie.genres.split("|") if movie.genres else []

    stats = movie.stats
    return {
        "name": movie.name or movie.title,
        "genre": genres,
        "release_year": movie.release_year,
        "number_user_rated": stats.number_user_rated if stats else 0,
        "average_rating": round(stats.average_rating, 2) if stats else 0.0,
    }


def _build_paginated_response(
    query,
    page: int,
    per_page: int,
    sort_by: str,
    sort_dir: str,
    default_sort_col,
) -> dict:
    """Apply sorting, COUNT, and LIMIT/OFFSET to a base SQLAlchemy query.

    Args:
        query:           A SQLAlchemy Query object with WHERE clauses already
                         applied but no ORDER BY / LIMIT / OFFSET yet.
        page:            1-indexed page number.
        per_page:        Number of rows per page. Expected to be pre-clamped
                         by the route layer (1–100).
        sort_by:         Column key to sort on. Resolved via _SORT_COLUMN_MAP;
                         falls back to default_sort_col if unknown.
        sort_dir:        'asc' or 'desc'.
        default_sort_col: ORM attribute used when sort_by is not recognised.

    Returns:
        Paginated envelope dict.
    """
    col = _SORT_COLUMN_MAP.get(sort_by, default_sort_col)
    order_expr = col.desc() if sort_dir == "desc" else col.asc()
    query = query.order_by(order_expr)

    # COUNT fires as SELECT COUNT(*) with the same WHERE — no LIMIT applied.
    total = query.count()

    offset = (page - 1) * per_page
    movies = query.offset(offset).limit(per_page).all()

    return {
        "data": [_serialize_movie(m) for m in movies],
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": math.ceil(total / per_page) if total > 0 else 0,
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def get_top_rated(
    page: int = 1,
    per_page: int = 25,
    sort_by: str = "average_rating",
    sort_dir: str = "desc",
) -> dict:
    """Return paginated movies with >10,000 ratings AND average rating > 4.0.

    This is the core business rule from the challenge requirements.
    Queries the pre-computed movie_stats table joined with movies.

    Args:
        page:     1-indexed page number.
        per_page: Number of results per page (pre-clamped by route layer).
        sort_by:  Column key — one of: name, release_year, average_rating,
                  number_user_rated. Defaults to average_rating.
        sort_dir: 'asc' or 'desc'. Defaults to 'desc'.

    Returns:
        Paginated envelope: {data, total, page, per_page, pages}.
    """
    query = (
        db.session.query(Movie)
        .join(MovieStats, Movie.movie_id == MovieStats.movie_id)
        .filter(
            MovieStats.number_user_rated > 10000,
            MovieStats.average_rating > 4.0,
        )
    )
    return _build_paginated_response(
        query,
        page,
        per_page,
        sort_by,
        sort_dir,
        default_sort_col=MovieStats.average_rating,
    )


def get_movie_details(name: str) -> dict | None:
    """Return detailed information for a movie by name.

    Uses case-insensitive partial matching to be user-friendly.

    Args:
        name: The movie name (or partial name) to search for.

    Returns:
        A serialized movie dict, or None if not found.
    """
    movie = (
        db.session.query(Movie)
        .join(MovieStats, Movie.movie_id == MovieStats.movie_id, isouter=True)
        .filter(Movie.name.ilike(f"%{name}%"))
        .first()
    )
    if not movie:
        return None
    return _serialize_movie(movie)


def search_movies(
    name: str | None = None,
    genre: str | None = None,
    year: int | None = None,
    min_rating: float | None = None,
    page: int = 1,
    per_page: int = 25,
    sort_by: str = "name",
    sort_dir: str = "asc",
) -> dict:
    """Search and filter movies by multiple optional parameters.

    Dynamically builds the query based on which filter parameters are provided.
    All filters are AND-combined. Results are paginated and sorted server-side.

    Args:
        name:      Partial movie name (case-insensitive).
        genre:     Genre to filter by (matches within pipe-delimited string).
        year:      Exact release year.
        min_rating: Minimum average rating threshold.
        page:      1-indexed page number.
        per_page:  Number of results per page (pre-clamped by route layer).
        sort_by:   Column key to sort on. Defaults to 'name'.
        sort_dir:  'asc' or 'desc'. Defaults to 'asc'.

    Returns:
        Paginated envelope: {data, total, page, per_page, pages}.
    """
    query = db.session.query(Movie).join(
        MovieStats, Movie.movie_id == MovieStats.movie_id, isouter=True
    )

    if name:
        query = query.filter(Movie.name.ilike(f"%{name}%"))

    if genre:
        # Match genre within pipe-delimited string
        # e.g., genre="Drama" matches "Comedy|Drama|Romance"
        query = query.filter(Movie.genres.ilike(f"%{genre}%"))

    if year:
        query = query.filter(Movie.release_year == year)

    if min_rating is not None:
        query = query.filter(MovieStats.average_rating >= min_rating)

    return _build_paginated_response(
        query,
        page,
        per_page,
        sort_by,
        sort_dir,
        default_sort_col=Movie.name,
    )
