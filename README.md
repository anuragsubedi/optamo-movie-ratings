# Movie Ratings Explorer

> A full-stack movie rating explorer application built with **Angular 19**, **Python/Flask**, and **SQLite**.

---

## Design Decisions & Architecture

### Backend Strategy

The raw dataset contains over 25 million ratings. Instead of loading this massive dataset into memory (via Pandas) on every server startup, we use a **hybrid data strategy**:

1. **One-Time Migration**: A raw Python script (`migrate.py`) bulk-inserts the CSV data into a persistent SQLite database.
2. **Pre-aggregation**: The migration pre-computes advanced aggregations (like average rating and total review counts per movie) into an indexed `movie_stats` table.
3. **REST API**: We use Flask and **SQLAlchemy ORM** to serve sub-millisecond API responses directly from the pre-aggregated database.

**To quickly inspect and test the available REST API endpoints, the application includes a fully integrated Swagger UI API Explorer at `/apidocs/`.**

### Frontend Design

The user interface is powered by **Angular 19**. It utilizes **Angular Material** for prebuilt components, RxJS for robust asynchronous state management, and functional Interceptors/Guards for a secure routing flow.

> **Read `design_notes.md` in the root directory for a comprehensive breakdown of architectural tradeoffs and decisions.**

---

## Quick Start

Ensure you have the following prerequisites installed:

- **`movie_ratings`** dataset folder extracted into the root directory (Files: `output_sample.json`, `ratings.csv`, `movies.csv`, `ratings_sample.csv`).
- **Python 3.9+** (Tested on 3.14)
- **Node.js 18+** (Tested on 24.12)

### Method A: Automated Setup (Recommended)

You can entirely automate the setup and booting of the application using the provided shell scripts natively, without requiring Docker.

**For macOS / Linux:**

```bash
# 1. Install dependencies & migrate the database
./shell_scripts/macos_linux_setup.sh

# 2. Boot up both servers
./shell_scripts/macos_linux_run.sh
```

**For Windows:**

```cmd
# 1. Install dependencies & migrate the database
.\shell_scripts\windows_setup.bat

# 2. Boot up both servers (Spawns separate terminal windows)
.\shell_scripts\windows_run.bat
```

> **Note:** To stop the automated servers on macOS/Linux, press `CTRL + C`. On Windows, simply close the spawned terminal windows.

---

### Method B: Manual Setup

To configure and run the services manually, you can do so by executing the commands below in separate terminal windows.

#### 1. Setup & Run Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate          # On Windows: call .venv\Scripts\activate.bat

pip install -r requirements.txt
python migrate.py                  # One-time CSV → SQLite migration (~60s)
python app.py                      # Starts the Flask API on port 5001
```

*Once running, visit `http://127.0.0.1:5001/apidocs/` to explore the API using Swagger!*

#### 2. Setup & Run Frontend

**Step 1: navigate to frontend directory**

```
cd frontend
```

**Step 2: Install Dependencies (run only once)**

```
npm install
```

**Step 3: Start the development server**

***Method A: Using npm (Standard)***

```
npm start
```

> *Why this works: Look at `frontend/package.json` under `"scripts"`. we will see `"start": "ng serve"`. Running `npm start` just triggers that command.*

***Method B: Using the Angular CLI directly (Via npx)***

```
npx ng serve
```

Once the terminal outputs `Application bundle generation complete` and prints out `http://localhost:4200/`, your frontend is securely running in its own standalone terminal!

### Use the Application

1. Open `http://localhost:4200` in your browser
2. Login with demo credentials: **admin** / **password**
3. Browse top-rated movies, search, and view details

---



## Architecture Overview

```
optamo-movie-ratings/
├── backend/                     # Flask API server
│   ├── app.py                   # App factory, blueprint registration, CORS
│   ├── config.py                # Configuration (DB path, JWT secret, CORS)
│   ├── models.py                # SQLAlchemy ORM models (Movie, MovieStats)
│   ├── migrate.py               # One-time CSV → SQLite migration script
│   ├── requirements.txt         # Python dependencies
│   ├── services/
│   │   ├── auth_service.py      # JWT token generation & validation
│   │   └── movie_service.py     # Business logic / query layer
│   └── routes/
│       ├── auth_routes.py       # POST /api/auth/login
│       └── movie_routes.py      # GET /api/movies/* endpoints
├── frontend/                    # Angular 19 SPA
│   └── src/app/
│       ├── components/
│       │   ├── login/           # Login form
│       │   ├── navbar/          # Navigation bar
│       │   ├── movie-list/      # Top-rated table + search
│       │   ├── movie-detail/    # Movie detail card
│       │   └── search-bar/      # Multi-param filter form
│       ├── services/
│       │   ├── auth.service.ts  # JWT token lifecycle
│       │   └── movie.service.ts # HTTP data access layer
│       ├── interceptors/        # Auth token auto-attachment
│       ├── guards/              # Route protection
│       └── models/              # TypeScript interfaces
|
├── movie_ratings/               # Source CSV data files
├── initial_exploration.ipynb    # Data exploration notebook
└── design_notes.md              # Architectural decisions log
```
