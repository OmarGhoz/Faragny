type Props = {
  movie: any;
  onClick?: () => void;
  size?: "normal" | "small";
};

export default function MovieCard({ movie, onClick, size = "normal" }: Props) {
  const poster = movie.poster_url || "";
  const rating = movie.vote_average ? movie.vote_average.toFixed(1) : null;
  const year = movie.release_date ? new Date(movie.release_date).getFullYear() : null;

  return (
    <div
      className="movie-card"
      onClick={onClick}
      style={size === "small" ? { width: 140 } : undefined}
    >
      {poster ? (
        <img
          src={poster}
          alt={movie.title}
          className="movie-card-poster"
          loading="lazy"
        />
      ) : (
        <div className="movie-card-placeholder">
          <span>🎬</span>
        </div>
      )}
      <div className="movie-card-info">
        <div className="movie-card-title">{movie.title}</div>
        <div className="movie-card-meta">
          {rating && <span className="movie-card-rating">★ {rating}</span>}
          {year && <span>{year}</span>}
        </div>
      </div>
    </div>
  );
}
