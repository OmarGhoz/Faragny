# FARAGNY - Movie Recommendation Platform

A full-stack movie recommendation platform with AI-powered semantic search, user authentication, and personalized watchlists.

## Features

- **Semantic Search**: Find movies by describing what you're looking for
- **User Authentication**: Register and login with secure password hashing
- **Personal Watchlist**: Save movies to your personal list
- **Movie Discovery**: Browse trending, top-rated, and genre-based collections
- **Where to Watch**: Quick links to find streaming availability

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - Database ORM
- **SQLite** - User database
- **ChromaDB** - Vector database for semantic search
- **LangChain + Ollama** - LLM integration for recommendations

### Frontend
- **React** - UI framework
- **TypeScript** - Type-safe JavaScript
- **Vite** - Build tool
- **Axios** - HTTP client

## Project Structure

```
├── backend/           # FastAPI backend
│   └── app/
│       ├── routers/   # API endpoints
│       ├── services/  # Business logic
│       ├── database.py
│       ├── models.py
│       └── main.py
├── frontend/          # React frontend
│   └── src/
│       ├── components/
│       ├── pages/
│       └── ...
├── data/              # Movie datasets
├── db/                # Database files (SQLite + Chroma)
├── notebooks/         # Jupyter notebooks
├── pipelines/         # Reusable ETL helpers
├── airflow/dags/      # Airflow DAGs (movie_data_pipeline)
└── requirements.txt   # Python dependencies
```

## Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+

### Backend Setup

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
cd backend
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

## Automated Data Pipeline (Airflow)

Automate the Kaggle → cleaning → vector refresh flow with the DAG in `airflow/dags/movie_data_pipeline.py`.

1. **Install dependencies**
   ```bash
   pip install pandas langchain-chroma langchain-ollama kaggle
   # Follow Airflow's official install guide (2.9+) for your environment
   ```
2. **Configure Kaggle credentials**
   - Place `kaggle.json` (API token) in `~/.kaggle/` and set permissions.
   - In Airflow, create a Variable named `kaggle_dataset_slug` with the dataset identifier (e.g. `tmdb/tmdb-movie-metadata`).
3. **Deploy the DAG**
   - Point `AIRFLOW_HOME` to this repo or copy `airflow/dags/movie_data_pipeline.py` into your Airflow DAGs folder.
   - Ensure Airflow workers have access to the project directory (the DAG imports `pipelines.*` modules).
4. **Run the pipeline**
   - Trigger manually from the Airflow UI or wait for the weekly schedule.
   - Tasks:
     1. `download_kaggle_dataset` – downloads & unzips into `data/`.
     2. `clean_dataset` – runs `pipelines.clean_data.clean_movies_dataset`.
     3. `refresh_vector_store` – rebuilds Chroma via `pipelines.update_vectors.refresh_vector_store`.

After a successful run, `data/processed_movies.csv` and `db/chroma_store/` are refreshed automatically.

## API Endpoints

- `POST /auth/register` - Register new user
- `POST /auth/login` - User login
- `GET /movies/search` - Search movies
- `GET /movies/filter` - Filter movies
- `GET /movies/{id}/similar` - Get similar movies
- `GET /watchlist` - Get user's watchlist
- `POST /watchlist/{movie_id}` - Add to watchlist
- `DELETE /watchlist/{movie_id}` - Remove from watchlist

## License

This project was created as part of the DEPI (Digital Egypt Pioneers Initiative) graduation project.

