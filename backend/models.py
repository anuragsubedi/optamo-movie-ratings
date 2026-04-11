"""
SQLAlchemy ORM models.

Defines the database schema using a code-first approach. The migration script
creates the underlying SQLite tables, and these models provide a clean,
type-hinted interface for querying at runtime.
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Movie(db.Model):
    """Movie entity with pre-parsed title components."""

    __tablename__ = "movies"

    movie_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)  # Original: "Toy Story (1995)"
    name = db.Column(db.String, index=True)  # Parsed: "Toy Story"
    release_year = db.Column(db.Integer)  # Parsed: 1995
    genres = db.Column(db.String)  # Pipe-delimited: "Adventure|Animation|Children"

    # One-to-one relationship with pre-computed stats
    stats = db.relationship(
        "MovieStats", uselist=False, backref="movie", lazy="joined"
    )

    def __repr__(self):
        return f"<Movie {self.movie_id}: {self.name} ({self.release_year})>"


class MovieStats(db.Model):
    """Pre-computed rating aggregations per movie.

    Materialized during migration to avoid runtime aggregation
    over 25M rating rows.
    """

    __tablename__ = "movie_stats"

    movie_id = db.Column(
        db.Integer, db.ForeignKey("movies.movie_id"), primary_key=True
    )
    average_rating = db.Column(db.Float)
    number_user_rated = db.Column(db.Integer)

    def __repr__(self):
        return (
            f"<MovieStats movie={self.movie_id} "
            f"avg={self.average_rating:.2f} count={self.number_user_rated}>"
        )
