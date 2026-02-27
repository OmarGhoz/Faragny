"""
Utility to rebuild the Chroma vector store from the processed movie dataset.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import List

import pandas as pd
from langchain.docstore.document import Document
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

from pipelines.clean_data import PROCESSED_DATA_PATH

PERSIST_DIR = Path("db/chroma_store")
COLLECTION_NAME = "movies"


def _load_movies(processed_path: Path) -> pd.DataFrame:
    if not processed_path.exists():
        raise FileNotFoundError(f"Processed dataset not found at {processed_path}")
    return pd.read_csv(processed_path)


def _to_documents(df: pd.DataFrame) -> List[Document]:
    documents: List[Document] = []
    for _, row in df.iterrows():
        description = row.get("overview") or ""
        title = row.get("title") or "Untitled"
        genres = row.get("genres") or []
        production = row.get("production_companies") or []
        metadata = {
            "id": int(row["id"]),
            "title": title,
            "genres": genres,
            "production_companies": production,
            "poster_url": row.get("poster_url"),
            "runtime": row.get("runtime"),
            "original_language": row.get("original_language"),
            "vote_average": row.get("vote_average"),
            "vote_count": row.get("vote_count"),
            "popularity": row.get("popularity"),
        }
        content = f"{title}\nGenres: {', '.join(genres)}\nOverview: {description}"
        documents.append(Document(page_content=content, metadata=metadata))
    return documents


def refresh_vector_store(processed_path: str | Path | None = None) -> None:
    """
    Rebuild the Chroma vector store from the processed dataset.
    """

    dataset_path = Path(processed_path) if processed_path else PROCESSED_DATA_PATH
    df = _load_movies(dataset_path)
    documents = _to_documents(df)

    if PERSIST_DIR.exists():
        shutil.rmtree(PERSIST_DIR)
    PERSIST_DIR.mkdir(parents=True, exist_ok=True)

    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    db = Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=str(PERSIST_DIR),
        embedding_function=embeddings,
    )
    db.add_documents(documents)
    db.persist()


__all__ = ["refresh_vector_store"]

