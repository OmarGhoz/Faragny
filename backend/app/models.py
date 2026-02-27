from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class Movie(BaseModel):
    id: int
    title: Optional[str] = None
    overview: Optional[str] = None
    genres: List[str] = []
    production_companies: List[str] = []
    poster_url: Optional[str] = None
    runtime: Optional[int] = None
    original_language: Optional[str] = None
    vote_average: Optional[float] = None
    vote_count: Optional[int] = None
    popularity: Optional[float] = None


class MovieListResponse(BaseModel):
    items: List[Movie]
    total: int
    limit: int
    offset: int


class SimilarTextRequest(BaseModel):
    overview: Optional[str] = ""
    genres: Optional[List[str]] = []
    production_companies: Optional[List[str]] = []
    k: int = 10


