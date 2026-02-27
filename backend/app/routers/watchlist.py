from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from sqlalchemy.orm import Session

from ..database import get_db, User, UserWatchlist
from ..services.data import get_movie_by_id
from .auth import get_current_user

router = APIRouter()


class WatchlistResponse(BaseModel):
    movie_ids: List[int]


class MessageResponse(BaseModel):
    message: str


class MovieResponse(BaseModel):
    id: int
    title: str | None = None
    overview: str | None = None
    genres: List[str] = []
    production_companies: List[str] = []
    poster_url: str | None = None
    runtime: int | None = None
    original_language: str | None = None
    vote_average: float | None = None
    vote_count: int | None = None
    popularity: float | None = None


class WatchlistMoviesResponse(BaseModel):
    items: List[MovieResponse]
    total: int


@router.get("", response_model=WatchlistMoviesResponse)
def get_watchlist(
    username: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all movies in user's watchlist."""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get all movie IDs from user's watchlist
    watchlist_items = db.query(UserWatchlist).filter(UserWatchlist.user_id == user.id).all()
    movie_ids = [item.movie_id for item in watchlist_items]
    
    # Fetch movie details for each ID
    movies = []
    for movie_id in movie_ids:
        movie_data = get_movie_by_id(movie_id)
        if movie_data:
            movies.append(movie_data)
    
    return WatchlistMoviesResponse(items=movies, total=len(movies))


@router.get("/ids", response_model=WatchlistResponse)
def get_watchlist_ids(
    username: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get just the movie IDs in user's watchlist (for checking if a movie is in list)."""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    watchlist_items = db.query(UserWatchlist).filter(UserWatchlist.user_id == user.id).all()
    movie_ids = [item.movie_id for item in watchlist_items]
    
    return WatchlistResponse(movie_ids=movie_ids)


@router.post("/{movie_id}", response_model=MessageResponse)
def add_to_watchlist(
    movie_id: int,
    username: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a movie to user's watchlist."""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if movie exists
    movie = get_movie_by_id(movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    # Check if already in watchlist
    existing = db.query(UserWatchlist).filter(
        UserWatchlist.user_id == user.id,
        UserWatchlist.movie_id == movie_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Movie already in watchlist")
    
    # Add to watchlist
    watchlist_item = UserWatchlist(user_id=user.id, movie_id=movie_id)
    db.add(watchlist_item)
    db.commit()
    
    return MessageResponse(message="Movie added to watchlist")


@router.delete("/{movie_id}", response_model=MessageResponse)
def remove_from_watchlist(
    movie_id: int,
    username: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove a movie from user's watchlist."""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Find and delete the watchlist item
    watchlist_item = db.query(UserWatchlist).filter(
        UserWatchlist.user_id == user.id,
        UserWatchlist.movie_id == movie_id
    ).first()
    
    if not watchlist_item:
        raise HTTPException(status_code=404, detail="Movie not in watchlist")
    
    db.delete(watchlist_item)
    db.commit()
    
    return MessageResponse(message="Movie removed from watchlist")

