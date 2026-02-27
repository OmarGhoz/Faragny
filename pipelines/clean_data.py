"""
Utilities for cleaning the Kaggle movie dataset.

The logic mirrors the existing preprocessing performed in notebooks so it can
run in automated contexts such as Airflow.
"""

from __future__ import annotations

from pathlib import Path
from ast import literal_eval
from collections.abc import Iterable
from typing import Iterable as TypingIterable

import pandas as pd

DATA_DIR = Path("data")
RAW_DATA_PATH = DATA_DIR / "data.csv"
PROCESSED_DATA_PATH = DATA_DIR / "processed_movies.csv"

REQUIRED_COLUMNS = {
    "id",
    "title",
    "overview",
}


def _to_name_list(value) -> list[str]:
    """Normalise list-like columns coming from Kaggle."""
    if isinstance(value, list):
        source = value
    elif pd.isna(value) or str(value).strip() == "":
        return []
    else:
        try:
            source = literal_eval(str(value))
        except (ValueError, SyntaxError):
            return [part.strip() for part in str(value).split(",") if part.strip()]

    if isinstance(source, dict):
        source = [source]
    elif not isinstance(source, Iterable) or isinstance(source, (str, bytes, int, float)):
        return []

    names: list[str] = []
    for item in source:
        if isinstance(item, dict) and "name" in item:
            names.append(str(item["name"]))
        else:
            names.append(str(item))
    return names


def _poster_url_from_path(poster_path: str | None) -> str | None:
    if not poster_path or str(poster_path).strip() == "":
        return None
    path = str(poster_path)
    if path.startswith("/"):
        return f"https://image.tmdb.org/t/p/w342{path}"
    if path.startswith("http://") or path.startswith("https://"):
        return path
    return f"/static/{path.replace(Path.sep, '/')}"


def clean_movies_dataset(
    raw_source: str | Path | None = None,
    output_path: str | Path | None = None,
) -> Path:
    """
    Clean the Kaggle dataset and export processed_movies.csv.

    Args:
        raw_source: Optional override for the raw CSV path.
        output_path: Optional override for the processed CSV path.
    Returns:
        Path to the processed dataset.
    """

    raw_file = Path(raw_source) if raw_source else RAW_DATA_PATH
    processed_file = Path(output_path) if output_path else PROCESSED_DATA_PATH

    if not raw_file.exists():
        raise FileNotFoundError(f"Raw dataset not found at {raw_file}")

    df = pd.read_csv(raw_file)
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise RuntimeError(f"Missing required columns in dataset: {sorted(missing)}")

    df["genres_list"] = df.get("genres", "").apply(_to_name_list)
    df["production_companies_list"] = df.get("production_companies", "").apply(_to_name_list)
    df["poster_url"] = df.get("poster_path").apply(_poster_url_from_path)

    for column in ("runtime", "vote_average", "vote_count", "popularity"):
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")

    df["id"] = pd.to_numeric(df["id"], errors="coerce").astype("Int64")
    df = df.dropna(subset=["id", "title"]).copy()

    columns_to_keep = [
        "id",
        "title",
        "overview",
        "genres_list",
        "production_companies_list",
        "poster_url",
        "runtime",
        "original_language",
        "vote_average",
        "vote_count",
        "popularity",
    ]

    final_df = df[columns_to_keep]
    final_df = final_df.rename(
        columns={
            "genres_list": "genres",
            "production_companies_list": "production_companies",
        }
    )

    processed_file.parent.mkdir(parents=True, exist_ok=True)
    final_df.to_csv(processed_file, index=False)
    return processed_file


__all__ = ["clean_movies_dataset", "RAW_DATA_PATH", "PROCESSED_DATA_PATH"]

