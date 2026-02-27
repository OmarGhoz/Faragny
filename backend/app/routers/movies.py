from typing import List, Optional
from fastapi import APIRouter, Query, HTTPException, Depends
from pydantic import BaseModel

from ..models import Movie, MovieListResponse, SimilarTextRequest
from ..services import data as data_svc
from ..services import vector as vector_svc
from .auth import get_current_user

router = APIRouter()


def _docs_to_movie_ids(docs) -> List[int]:
    ids: List[int] = []
    for d in docs:
        mid = d.metadata.get("movie_id") if hasattr(d, "metadata") else None
        if isinstance(mid, (int, float)) and mid == mid:  # not NaN
            ids.append(int(mid))
    return ids


# Static routes MUST come before dynamic /{movie_id} route
@router.get("/search", response_model=MovieListResponse)
def search_movies(
    q: str = Query(..., description="Query text"),
    mode: str = Query("auto", regex="^(auto|title|semantic)$"),
    limit: int = 20,
    user: str = Depends(get_current_user),
):
    items: List[dict]
    total: int

    if mode in ("title", "auto"):
        title_hits = data_svc.search_title(q, limit=limit)
        if mode == "title" or (mode == "auto" and len(title_hits) > 0):
            items = title_hits
            total = len(title_hits)
            return MovieListResponse(items=[Movie(**m) for m in items], total=total, limit=limit, offset=0)

    # semantic fallback
    docs = vector_svc.search_similar(q, k=limit)
    ids = _docs_to_movie_ids(docs)
    # Fetch movies by id (dedupe while preserving order)
    seen = set()
    movies: List[dict] = []
    for mid in ids:
        if mid in seen:
            continue
        seen.add(mid)
        m = data_svc.get_movie_by_id(mid)
        if m:
            movies.append(m)
    items = movies
    total = len(items)
    return MovieListResponse(items=[Movie(**m) for m in items], total=total, limit=limit, offset=0)


@router.get("/filter", response_model=MovieListResponse)
def filter_endpoint(
    genres: Optional[List[str]] = Query(default=None),
    production_companies: Optional[List[str]] = Query(default=None),
    runtime_min: Optional[int] = None,
    runtime_max: Optional[int] = None,
    language: Optional[str] = None,
    vote_average_min: Optional[float] = None,
    vote_count_min: Optional[int] = None,
    popularity_min: Optional[float] = None,
    limit: int = 20,
    offset: int = 0,
    user: str = Depends(get_current_user),
):
    items, total = data_svc.filter_movies(
        genres=genres,
        production_companies=production_companies,
        runtime_min=runtime_min,
        runtime_max=runtime_max,
        language=language,
        vote_average_min=vote_average_min,
        vote_count_min=vote_count_min,
        popularity_min=popularity_min,
        limit=limit,
        offset=offset,
    )
    return MovieListResponse(items=[Movie(**m) for m in items], total=total, limit=limit, offset=offset)


@router.get("/facets")
def facets(user: str = Depends(get_current_user)):
    return data_svc.facets()


@router.post("/similar-text", response_model=MovieListResponse)
def similar_by_text(payload: SimilarTextRequest, user: str = Depends(get_current_user)):
    text = " ".join(
        filter(
            None,
            [
                payload.overview or "",
                ", ".join(payload.genres or []),
                ", ".join(payload.production_companies or []),
            ],
        )
    )
    docs = vector_svc.search_similar(text, k=payload.k)
    ids = _docs_to_movie_ids(docs)
    items = []
    for mid in ids:
        m = data_svc.get_movie_by_id(mid)
        if m:
            items.append(m)
    return MovieListResponse(items=[Movie(**m) for m in items], total=len(items), limit=payload.k, offset=0)


# Dynamic routes with path parameters MUST come after static routes
@router.get("/{movie_id}", response_model=Movie)
def get_movie(movie_id: int, user: str = Depends(get_current_user)):
    movie = data_svc.get_movie_by_id(movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie


@router.get("/{movie_id}/similar", response_model=MovieListResponse)
def similar_movies(movie_id: int, k: int = 10, user: str = Depends(get_current_user)):
    base = data_svc.get_movie_by_id(movie_id)
    if not base:
        raise HTTPException(status_code=404, detail="Movie not found")
    text = " ".join(
        filter(
            None,
            [
                base.get("overview") or "",
                ", ".join(base.get("genres") or []),
                ", ".join(base.get("production_companies") or []),
            ],
        )
    )
    docs = vector_svc.search_similar(text, k=k + 5)  # fetch a bit more to filter out self
    ids = _docs_to_movie_ids(docs)
    items: List[dict] = []
    seen = {movie_id}
    for mid in ids:
        if mid in seen:
            continue
        seen.add(mid)
        m = data_svc.get_movie_by_id(mid)
        if m:
            items.append(m)
        if len(items) >= k:
            break
    return MovieListResponse(items=[Movie(**m) for m in items], total=len(items), limit=k, offset=0)
