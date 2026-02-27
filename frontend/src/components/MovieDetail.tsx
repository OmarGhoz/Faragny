import { useEffect, useState } from "react";
import { api } from "../api";
import MovieCard from "./MovieCard";

type Props = {
  movie: any | null;
  onClose: () => void;
  onSelectMovie: (movie: any) => void;
  watchlistIds: number[];
  onWatchlistChange: () => void;
};

export default function MovieDetail({ 
  movie, 
  onClose, 
  onSelectMovie, 
  watchlistIds,
  onWatchlistChange 
}: Props) {
  const [similar, setSimilar] = useState<any[]>([]);
  const [loadingSimilar, setLoadingSimilar] = useState(false);
  const [addingToList, setAddingToList] = useState(false);

  const isInWatchlist = movie ? watchlistIds.includes(movie.id) : false;

  useEffect(() => {
    if (movie?.id) {
      setSimilar([]);
      setLoadingSimilar(true);
      api
        .get(`/movies/${movie.id}/similar`, { params: { k: 12 } })
        .then(({ data }) => {
          setSimilar(data.items || []);
        })
        .catch(() => {})
        .finally(() => setLoadingSimilar(false));
    }
  }, [movie?.id]);

  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    document.addEventListener("keydown", handleEsc);
    return () => document.removeEventListener("keydown", handleEsc);
  }, [onClose]);

  async function handleToggleWatchlist() {
    if (!movie || addingToList) return;
    
    setAddingToList(true);
    try {
      if (isInWatchlist) {
        await api.delete(`/watchlist/${movie.id}`);
      } else {
        await api.post(`/watchlist/${movie.id}`);
      }
      onWatchlistChange();
    } catch (err) {
      console.error("Failed to update watchlist:", err);
    } finally {
      setAddingToList(false);
    }
  }

  if (!movie) return null;

  const rating = movie.vote_average ? movie.vote_average.toFixed(1) : null;
  const year = movie.release_date
    ? new Date(movie.release_date).getFullYear()
    : null;
  const runtime = movie.runtime ? `${movie.runtime} min` : null;
  const backdropUrl =
    movie.backdrop_url ||
    movie.poster_url ||
    "";

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-hero">
          {backdropUrl && (
            <div
              className="modal-hero-bg"
              style={{ backgroundImage: `url(${backdropUrl})` }}
            />
          )}
          <button className="modal-close" onClick={onClose}>
            ✕
          </button>
          <div className="modal-hero-content">
            <h2 className="modal-title">{movie.title}</h2>
            <div className="modal-actions">
              <button 
                className="modal-btn primary"
                onClick={() => window.open(`https://www.google.com/search?q=Where+to+watch+${encodeURIComponent(movie.title)}`, '_blank')}
              >
                ▶ Where to Watch
              </button>
              <button 
                className={`modal-btn ${isInWatchlist ? "in-list" : "secondary"}`}
                onClick={handleToggleWatchlist}
                disabled={addingToList}
              >
                {addingToList 
                  ? "..." 
                  : isInWatchlist 
                    ? "✓ In My List" 
                    : "+ My List"}
              </button>
            </div>
          </div>
        </div>

        <div className="modal-body">
          <div className="modal-meta">
            {rating && (
              <span className="modal-rating">★ {rating}</span>
            )}
            {year && <span className="modal-year">{year}</span>}
            {runtime && <span className="modal-runtime">{runtime}</span>}
          </div>

          <p className="modal-overview">
            {movie.overview || "No overview available."}
          </p>

          <div className="modal-details">
            <div className="modal-detail-item">
              <div className="modal-detail-label">Genres</div>
              <div className="modal-detail-value">
                {Array.isArray(movie.genres)
                  ? movie.genres.join(", ")
                  : movie.genres || "—"}
              </div>
            </div>
            <div className="modal-detail-item">
              <div className="modal-detail-label">Production</div>
              <div className="modal-detail-value">
                {Array.isArray(movie.production_companies)
                  ? movie.production_companies.slice(0, 3).join(", ")
                  : movie.production_companies || "—"}
              </div>
            </div>
            <div className="modal-detail-item">
              <div className="modal-detail-label">Language</div>
              <div className="modal-detail-value">
                {movie.original_language?.toUpperCase() || "—"}
              </div>
            </div>
            <div className="modal-detail-item">
              <div className="modal-detail-label">Popularity</div>
              <div className="modal-detail-value">
                {movie.popularity ? movie.popularity.toFixed(0) : "—"}
              </div>
            </div>
          </div>

          <div className="modal-similar-section">
            <h3 className="modal-similar-title">More Like This</h3>
            {loadingSimilar ? (
              <div className="modal-similar-loading">
                <div className="spinner" />
              </div>
            ) : similar.length > 0 ? (
              <div className="modal-similar-grid">
                {similar.map((m) => (
                  <MovieCard
                    key={m.id}
                    movie={m}
                    size="small"
                    onClick={() => onSelectMovie(m)}
                  />
                ))}
              </div>
            ) : (
              <div className="modal-similar-loading" style={{ color: "#666" }}>
                No similar movies found
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
