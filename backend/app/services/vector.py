from typing import List, Dict, Any
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

PERSIST_DIR = "db/chroma_store"

_embeddings = OllamaEmbeddings(model="nomic-embed-text")
_db = Chroma(persist_directory=PERSIST_DIR, embedding_function=_embeddings)


def search_similar(text: str, k: int = 10):
    return _db.similarity_search(text, k=k)


def get_raw(limit: int = 5) -> Dict[str, Any]:
    return _db.get(limit=limit)


