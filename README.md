# Movie Ratings Explorer

> Full-stack movie rating explorer application built with **Angular**, **Python/Flask**, and **SQLite**

---

## Quick Start

### Prerequisites

- **`movie_ratings`** dataset folder extracted into the root directory - Files: ['output_sample.json', 'ratings.csv', 'movies.csv', 'ratings_sample.csv']
- **Python 3.9+** (tested with 3.14.2)


### 1. Setup Backend

```bash
# Create virtual environment
cd backend
python3 -m venv .venv
source .venv/bin/activate          # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run one-time data migration (CSV → SQLite, ~30 seconds)
python migrate.py

# Start the Flask server
python app.py
# → Running on http://127.0.0.1:5000
```
