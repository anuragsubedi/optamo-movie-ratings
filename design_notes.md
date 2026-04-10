# Design Notes - Movie Ratings Platform

---

## 1. Data Layer Strategy - SQLite with Pre-Computed Aggregations

### Problem

The `ratings.csv` contains **25 million rows (~678 MB)**. We need a strategy that makes API queries fast and at the same time doesn't add to the server startup time

***Option 1 (Load entire dataset into memory using `pandas`)*** - While we have a very simple dataset with only 2 tables and very few columns, the `ratings.csv` file is extremely large and contains millions of rows. This means that the memory footprint will be very large if we load the full dataframe in RAM. It also requires ~30s of startup time since we have to reload CSV on every restart.

***Option 2 (SQLite with migration script)*** - SQLite doesn't load the entire database into RAM, it uses a hybrid page-cache approach where only the pages (4KB blocks) actively being queried are kept in memory. It also has proper table indexing and is optimized for efficient relational joins. An index on our lookup column "moveId"  might allow very efficient retrieval.

***Option 3 (Standalone Database server)*** - While a standalone database server (PostgreSQL/MySQL) is vastly superior. It is beyond the scope of this usecase.

### Decision: SQLite + One-Time Migration Script

A `migrate.py` script loads CSVs into a SQLite database file (`movie_ratings.db`) once. The Flask app connects to this persistent file on every startup — **instant boot, zero data loading**.

#### Strategy:

- **Migration** (one-time bulk insert) using sqlite3 module - Raw `executemany()` with batched inserts: ~30-60 seconds.
- API Queries (runtime) - `SQLAlchemy` ORM - Clean, maintainable, code-first approach

## 2. Title Parsing Strategy

Movie titles in the CSV follows the pattern `Movie Name (YYYY)`. We can use regex to strategically extract the year:

- Movies without year: `name = full_title, year = None`
- Movies with parenthetical content that isn't a year: regex anchored to end of string with `$`

Parsing happens **during migration**, not at query time, each movie gets `name` and `release_year` columns.

---

## 3. Genre Handling

Genres are stored as pipe-delimited strings (e.g., `"Adventure|Animation|Children"`) in the database. Splitting to arrays happens at **serialization time** in the service layer.

### Why not normalize genres into a separate table?

- The API never queries "all movies of genre X" as a primary use case, genre is just a filter parameter.
- A normalized `movie_genres` junction table would require complex many-to-many joins for every API call
- SQLite's `LIKE '%Genre%'` on the pipe-delimited string is sufficient for filtering and fast with the small dataset which keeps the schema simple

## 4. RESTful API Design

### Endpoint Structure

```
/api/movies/top-rated    → GET  (collection, pre-filtered by business rules)
/api/movies/details      → GET  (single resource by query param)
/api/movies/search       → GET  (collection, user-filtered)
/api/auth/login          → POST (action, creates session token)
```

### Response Format

All movie endpoints return the same shape matching `output_sample.json`:

```json
{
  "name": "string",
  "genre": ["string"],
  "release_year": number | null,
  "number_user_rated": number,
  "average_rating": number
}
```

---

## 5. Authentication

I plan to setup a minimal and stateless JWT token authentication which can be extended in the future as per need.

1. `POST /api/auth/login` accepts hardcoded `admin/password` → returns signed JWT
2. `@token_required` decorator on protected routes validates the token
3. Angular `AuthInterceptor` auto-attaches tokens, `AuthGuard` protects routes

---

## 6. Angular Frontend Architecture

### Component Hierarchy

```
AppComponent
├── NavbarComponent
├── LoginComponent
├── MovieListComponent
│   └── SearchBarComponent
└── MovieDetailComponent
```

### Using Angular Material for design

Angular material is an official library that provides ready-to use components for tables, buttons, etc. This helps me avoid additional custom CSS boilerplate.
