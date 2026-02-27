from __future__ import annotations

from typing import List, Dict, Any, Optional, Tuple
import os
import pandas as pd
from ast import literal_eval
from collections.abc import Iterable

DATA_CSV_PATH = os.path.join("data", "processed_movies.csv")

_df: Optional[pd.DataFrame] = None


def _to_name_list(value) -> List[str]:
    if isinstance(value, list):
        source = value
    elif pd.isna(value) or str(value).strip() == "":
        return []
    else:
        try:
            source = literal_eval(value)
        except (ValueError, SyntaxError):
            return [part.strip() for part in str(value).split(",") if part.strip()]

    if isinstance(source, dict):
        source = [source]
    elif not isinstance(source, Iterable) or isinstance(source, (str, bytes, int, float)):
        return []

    names = []
    for item in source:
        if isinstance(item, dict) and "name" in item:
            names.append(str(item["name"]))
        else:
            names.append(str(item))
    return names


def _poster_url_from_path(poster_path: str | None) -> Optional[str]:
    if not poster_path or str(poster_path).strip() == "":
        return None
    path = str(poster_path)
    # Remote TMDB style: /abc.jpg
    if path.startswith("/"):
        return f"https://image.tmdb.org/t/p/w342{path}"
    # Absolute http(s)
    if path.startswith("http://") or path.startswith("https://"):
        return path
    # Treat as local relative to data/
    # Expose via /static/<relative-path>
    return f"/static/{path.replace(os.sep, '/')}"


def load_dataframe() -> pd.DataFrame:
    global _df
    if _df is not None:
        return _df
    usecols = [
        "id",
        "title",
        "overview",
        "genres",
        "production_companies",
        "poster_path",
        "runtime",
        "original_language",
        "vote_average",
        "vote_count",
        "popularity",
    ]
    df = pd.read_csv(DATA_CSV_PATH, usecols=[c for c in usecols if os.path.exists(DATA_CSV_PATH)])
    # Ensure required minimal columns exist
    required = {"id", "title", "overview"}
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise RuntimeError(f"Missing required columns in processed_movies.csv: {missing}")

    # Normalize lists
    df["genres_list"] = df.get("genres", "").apply(_to_name_list) if "genres" in df.columns else [[]]
    df["production_companies_list"] = (
        df.get("production_companies", "").apply(_to_name_list) if "production_companies" in df.columns else [[]]
    )
    # Poster URL
    df["poster_url"] = df.get("poster_path").apply(_poster_url_from_path) if "poster_path" in df.columns else None

    # Types
    df["id"] = df["id"].astype(int, errors="ignore")

    _df = df
    return _df


def get_movie_by_id(movie_id: int) -> Optional[Dict[str, Any]]:
    df = load_dataframe()
    row = df.loc[df["id"] == movie_id]
    if row.empty:
        return None
    return _row_to_movie(row.iloc[0])


def search_title(q: str, limit: int = 20) -> List[Dict[str, Any]]:
    df = load_dataframe()
    mask = df["title"].str.contains(q, case=False, na=False)
    rows = df[mask].head(limit)
    return [_row_to_movie(r) for _, r in rows.iterrows()]


def filter_movies(
    genres: Optional[List[str]] = None,
    production_companies: Optional[List[str]] = None,
    runtime_min: Optional[int] = None,
    runtime_max: Optional[int] = None,
    language: Optional[str] = None,
    vote_average_min: Optional[float] = None,
    vote_count_min: Optional[int] = None,
    popularity_min: Optional[float] = None,
    limit: int = 20,
    offset: int = 0,
) -> Tuple[List[Dict[str, Any]], int]:
    df = load_dataframe()
    filt = pd.Series([True] * len(df), index=df.index)

    if genres:
        genres_lower = {g.strip().lower() for g in genres}
        filt &= df["genres_list"].apply(lambda lst: bool(genres_lower.intersection({x.lower() for x in lst})))
    if production_companies:
        companies_lower = {c.strip().lower() for c in production_companies}
        filt &= df["production_companies_list"].apply(
            lambda lst: bool(companies_lower.intersection({x.lower() for x in lst}))
        )
    if runtime_min is not None and "runtime" in df.columns:
        filt &= df["runtime"].fillna(0) >= runtime_min
    if runtime_max is not None and "runtime" in df.columns:
        filt &= df["runtime"].fillna(10_000) <= runtime_max
    if language and "original_language" in df.columns:
        filt &= df["original_language"].fillna("").str.lower() == language.lower()
    if vote_average_min is not None and "vote_average" in df.columns:
        filt &= df["vote_average"].fillna(0) >= vote_average_min
    if vote_count_min is not None and "vote_count" in df.columns:
        filt &= df["vote_count"].fillna(0) >= vote_count_min
    if popularity_min is not None and "popularity" in df.columns:
        filt &= df["popularity"].fillna(0) >= popularity_min

    filtered = df[filt]
    total = len(filtered)
    
    # Sort by popularity descending to show best movies first
    if "popularity" in filtered.columns:
        filtered = filtered.sort_values("popularity", ascending=False)
    
    page = filtered.iloc[offset : offset + limit]
    items = [_row_to_movie(r) for _, r in page.iterrows()]
    return items, total


def facets() -> Dict[str, List[str]]:
    df = load_dataframe()
    all_genres = sorted({g for lst in df["genres_list"] for g in lst})
    all_companies = sorted({c for lst in df["production_companies_list"] for c in lst})
    languages = sorted(df["original_language"].dropna().astype(str).str.lower().unique().tolist()) if "original_language" in df.columns else []
    return {
        "genres": all_genres,
        "production_companies": all_companies,
        "languages": languages,
    }


def _row_to_movie(row: pd.Series) -> Dict[str, Any]:
    return {
        "id": int(row["id"]),
        "title": row.get("title"),
        "overview": row.get("overview"),
        "genres": row.get("genres_list", []),
        "production_companies": row.get("production_companies_list", []),
        "poster_url": row.get("poster_url"),
        "runtime": row.get("runtime"),
        "original_language": row.get("original_language"),
        "vote_average": row.get("vote_average"),
        "vote_count": row.get("vote_count"),
        "popularity": row.get("popularity"),
    }


