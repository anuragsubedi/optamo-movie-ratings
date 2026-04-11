"""
One-time CSV → SQLite migration script.

Reads movies.csv and ratings.csv, creates the SQLite database with proper
schema, indexes, and a pre-computed movie_stats aggregation table.
"""

import csv
import os
import re
import sqlite3
import time

from config import Config

def parse_title(title: str) -> tuple[str, int | None]:
    """Extract clean name and release year from a title like 'Toy Story (1995)'.

    Returns:
        (name, year) tuple. Year is None if not parseable.
    """
    match = re.search(r"\((\d{4})\)\s*$", title.strip())
    if match:
        year = int(match.group(1))
        name = re.sub(r"\s*\(\d{4}\)\s*$", "", title.strip())
        return name, year
    return title.strip(), None


def migrate():
    """Execute the full CSV -> SQLite migration."""
    db_path = Config.DB_PATH
    csv_dir = Config.CSV_DATA_DIR

    # Safety: don't accidentally overwrite an existing database
    if os.path.exists(db_path):
        response = input(
            f"Database already exists at {db_path}. Overwrite? [y/N]: "
        )
        if response.lower() != "y":
            print("Migration cancelled.")
            return
        os.remove(db_path)

    print(f"Creating database at: {db_path}")
    print(f"Reading CSVs from: {csv_dir}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Enable WAL mode and increase page size for better write performance
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA page_size=4096")
    cursor.execute("PRAGMA synchronous=OFF")  # Safe for one-time migration

    # ── Step 1: Create tables ──
    print("\n[1/5] Creating tables...")

    cursor.execute(
        """
        CREATE TABLE movies (
            movie_id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            name TEXT,
            release_year INTEGER,
            genres TEXT
        )
    """
    )

    cursor.execute(
        """
        CREATE TABLE ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            movie_id INTEGER NOT NULL,
            rating REAL NOT NULL,
            timestamp INTEGER,
            FOREIGN KEY (movie_id) REFERENCES movies(movie_id)
        )
    """
    )

    # ── Step 2: Load movies ──
    print("[2/5] Loading movies.csv...")
    movies_path = os.path.join(csv_dir, "movies.csv")
    movie_count = 0

    with open(movies_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        batch = []
        for row in reader:
            title = row["title"].strip()
            name, year = parse_title(title)
            genres = row["genres"].strip()

            # Normalize "(no genres listed)" to empty string
            if genres == "(no genres listed)":
                genres = ""

            batch.append(
                (int(row["movieId"]), title, name, year, genres)
            )
            movie_count += 1

        cursor.executemany(
            "INSERT INTO movies (movie_id, title, name, release_year, genres) "
            "VALUES (?, ?, ?, ?, ?)",
            batch,
        )

    conn.commit()
    print(f"  → Inserted {movie_count:,} movies")

    # ── Step 3: Load ratings (batched) ──
    print("[3/5] Loading ratings.csv (this takes ~30-60 seconds)...")
    ratings_path = os.path.join(csv_dir, "ratings.csv")
    rating_count = 0
    batch_size = 100_000
    batch = []
    start_time = time.time()

    with open(ratings_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            batch.append(
                (
                    int(row["userId"]),
                    int(row["movieId"]),
                    float(row["rating"]),
                    int(row["timestamp"]),
                )
            )
            rating_count += 1

            if len(batch) >= batch_size:
                cursor.executemany(
                    "INSERT INTO ratings (user_id, movie_id, rating, timestamp) "
                    "VALUES (?, ?, ?, ?)",
                    batch,
                )
                conn.commit()
                batch.clear()
                elapsed = time.time() - start_time
                print(
                    f"  → {rating_count:>12,} ratings loaded "
                    f"({elapsed:.1f}s elapsed)",
                    end="\r",
                )

    # Insert remaining batch
    if batch:
        cursor.executemany(
            "INSERT INTO ratings (user_id, movie_id, rating, timestamp) "
            "VALUES (?, ?, ?, ?)",
            batch,
        )
        conn.commit()

    elapsed = time.time() - start_time
    print(f"\n  → Inserted {rating_count:,} ratings in {elapsed:.1f}s")

    # ── Step 4: Create movie_stats aggregation table ──
    print("[4/5] Computing movie_stats aggregation table...")
    agg_start = time.time()

    cursor.execute(
        """
        CREATE TABLE movie_stats AS
        SELECT
            movie_id,
            ROUND(AVG(rating), 2) as average_rating,
            COUNT(*) as number_user_rated
        FROM ratings
        GROUP BY movie_id
    """
    )
    conn.commit()

    stats_count = cursor.execute("SELECT COUNT(*) FROM movie_stats").fetchone()[0]
    agg_elapsed = time.time() - agg_start
    print(f"  → Computed stats for {stats_count:,} movies in {agg_elapsed:.1f}s")

    # ── Step 5: Create indexes ──
    print("[5/5] Creating indexes...")

    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_movie_stats_movie_id "
        "ON movie_stats(movie_id)"
    )
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_ratings_movie_id "
        "ON ratings(movie_id)"
    )
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_movies_name "
        "ON movies(name)"
    )
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_movies_release_year "
        "ON movies(release_year)"
    )
    conn.commit()

    # ── Verification ──
    print("\n  Migration complete!")
    print(f"   Database: {db_path}")
    print(f"   Size: {os.path.getsize(db_path) / 1e6:.1f} MB")
    print(f"   Movies: {movie_count:,}")
    print(f"   Ratings: {rating_count:,}")
    print(f"   Movie stats: {stats_count:,}")
    print(f"   Total time: {time.time() - start_time:.1f}s")

    # Quick sanity check
    top_rated_count = cursor.execute(
        """
        SELECT COUNT(*) FROM movies m
        JOIN movie_stats ms ON m.movie_id = ms.movie_id
        WHERE ms.number_user_rated > 10000 AND ms.average_rating > 4.0
    """
    ).fetchone()[0]
    print(f"\n   Movies with >10K ratings AND avg > 4.0: {top_rated_count}")

    conn.close()


if __name__ == "__main__":
    migrate()
