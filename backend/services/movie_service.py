"""
Movie service — business logic layer.

Encapsulates all data access and transformation logic for movie-related
endpoints. Components (routes) call these functions instead of writing
queries directly, maintaining clean separation of concerns.
"""

from models import Movie, MovieStats, db


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
    genres = (
        movie.genres.split("|") if movie.genres else []
    )

    stats = movie.stats
    return {
        "name": movie.name or movie.title,
        "genre": genres,
        "release_year": movie.release_year,
        "number_user_rated": stats.number_user_rated if stats else 0,
        "average_rating": round(stats.average_rating, 2) if stats else 0.0,
    }


def get_top_rated() -> list[dict]:
    """Return movies with >10,000 ratings AND average rating > 4.0.

    This is the core business rule from the challenge requirements.
    Queries the pre-computed movie_stats table joined with movies.
    """
    movies = (
        db.session.query(Movie)
        .join(MovieStats, Movie.movie_id == MovieStats.movie_id)
        .filter(
            MovieStats.number_user_rated > 10000,
            MovieStats.average_rating > 4.0,
        )
        .order_by(MovieStats.average_rating.desc())
        .all()
    )
    return [_serialize_movie(m) for m in movies]


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
) -> list[dict]:
    """Search and filter movies by multiple optional parameters.

    Dynamically builds the query based on which parameters are provided.
    All filters are AND-combined.

    Args:
        name: Partial movie name (case-insensitive).
        genre: Genre to filter by (matches within pipe-delimited string).
        year: Exact release year.
        min_rating: Minimum average rating threshold.

    Returns:
        List of serialized movie dicts matching all provided filters.
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

    # Limit results to prevent overwhelming the frontend
    movies = query.order_by(Movie.name).limit(100).all()
    return [_serialize_movie(m) for m in movies]
