from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .database import init_db


def create_app() -> FastAPI:
    app = FastAPI(title="Movie Recommendation Platform")

    # Open CORS for MVP; restrict in production
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Serve local assets (e.g., posters) from the data folder if available
    app.mount("/static", StaticFiles(directory="data"), name="static")

    # Routers are registered in run_app to avoid circular imports on module import
    return app


app = create_app()


def run_app() -> FastAPI:
    # Initialize database tables
    init_db()
    
    # Import routers here to ensure app is created first
    from .routers.auth import router as auth_router
    from .routers.movies import router as movies_router
    from .routers.watchlist import router as watchlist_router

    app.include_router(auth_router, prefix="/auth", tags=["auth"])
    app.include_router(movies_router, prefix="/movies", tags=["movies"])
    app.include_router(watchlist_router, prefix="/watchlist", tags=["watchlist"])
    return app


# Ensure routers are mounted when running via uvicorn
run_app()


