import { useEffect, useState, useRef, useCallback } from "react";
import { api } from "../api";
import MovieCard from "../components/MovieCard";
import MovieDetail from "../components/MovieDetail";
import SearchBar from "../components/SearchBar";
import { setAuth, getAuth } from "../store";

type SearchMode = "auto" | "title" | "semantic";

// Genre categories for Netflix-style rows
// Each row fetches extra movies so we can deduplicate across rows
const GENRE_ROWS = [
  { title: "Trending Now", params: { popularity_min: 50, limit: 40 } },
  { title: "Top Rated", params: { vote_average_min: 7.5, vote_count_min: 500, limit: 40 } },
  { title: "Action & Adventure", params: { genres: ["Action"], limit: 40 } },
  { title: "Comedy", params: { genres: ["Comedy"], limit: 40 } },
  { title: "Drama", params: { genres: ["Drama"], limit: 40 } },
  { title: "Sci-Fi & Fantasy", params: { genres: ["Science Fiction"], limit: 40 } },
  { title: "Horror", params: { genres: ["Horror"], limit: 40 } },
  { title: "Romance", params: { genres: ["Romance"], limit: 40 } },
  { title: "Animation", params: { genres: ["Animation"], limit: 40 } },
  { title: "Thriller", params: { genres: ["Thriller"], limit: 40 } },
];

export default function Catalog() {
  const [q, setQ] = useState("");
  const [mode, setMode] = useState<SearchMode>("auto");
  const [searchResults, setSearchResults] = useState<any[] | null>(null);
  const [selected, setSelected] = useState<any | null>(null);
  const [loading, setLoading] = useState(false);
  const [rows, setRows] = useState<{ title: string; movies: any[] }[]>([]);
  const [heroMovie, setHeroMovie] = useState<any | null>(null);
  const [scrolled, setScrolled] = useState(false);
  const [watchlist, setWatchlist] = useState<any[]>([]);
  const [watchlistIds, setWatchlistIds] = useState<number[]>([]);

  const auth = getAuth();

  // Handle scroll for navbar background
  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 50);
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  // Fetch watchlist
  const fetchWatchlist = useCallback(async () => {
    try {
      const { data } = await api.get("/watchlist");
      setWatchlist(data.items || []);
      setWatchlistIds((data.items || []).map((m: any) => m.id));
    } catch (err) {
      console.error("Failed to fetch watchlist:", err);
      setWatchlist([]);
      setWatchlistIds([]);
    }
  }, []);

  // Load watchlist on mount
  useEffect(() => {
    fetchWatchlist();
  }, [fetchWatchlist]);

  // Load initial genre rows with deduplication
  useEffect(() => {
    async function loadRows() {
      const rawResults = await Promise.all(
        GENRE_ROWS.map(async (row) => {
          try {
            const { data } = await api.get("/movies/filter", { params: row.params });
            return { title: row.title, movies: data.items || [] };
          } catch {
            return { title: row.title, movies: [] };
          }
        })
      );

      // Deduplicate: each movie appears only in the first row it's found
      const seenIds = new Set<number>();
      const deduped = rawResults.map((row) => {
        const uniqueMovies = row.movies.filter((m: any) => {
          if (seenIds.has(m.id)) return false;
          seenIds.add(m.id);
          return true;
        });
        return { title: row.title, movies: uniqueMovies.slice(0, 20) };
      });

      setRows(deduped.filter((r) => r.movies.length > 0));

      // Set hero from trending
      const trending = deduped.find((r) => r.title === "Trending Now");
      if (trending && trending.movies.length > 0) {
        const randomIndex = Math.floor(Math.random() * Math.min(5, trending.movies.length));
        setHeroMovie(trending.movies[randomIndex]);
      }
    }
    loadRows();
  }, []);

  async function runSearch() {
    if (!q.trim()) {
      setSearchResults(null);
      return;
    }
    setLoading(true);
    try {
      const { data } = await api.get("/movies/search", {
        params: { q, mode, limit: 30 },
      });
      setSearchResults(data.items || []);
    } finally {
      setLoading(false);
    }
  }

  function handleSelectMovie(movie: any) {
    setSelected(movie);
  }

  // Find the index of "Top Rated" row to insert "My List" after it
  const topRatedIndex = rows.findIndex((r) => r.title === "Top Rated");

  return (
    <>
      {/* Navbar */}
      <nav className={`navbar ${scrolled ? "scrolled" : ""}`}>
        <div className="navbar-brand">FARAGNY</div>
        <div className="navbar-right">
          <SearchBar
            q={q}
            setQ={setQ}
            mode={mode}
            setMode={setMode}
            onSearch={runSearch}
          />
          <div className="navbar-user">
            <div className="avatar">{auth.username?.[0]?.toUpperCase() || "U"}</div>
            <span>{auth.username}</span>
          </div>
          <button
            className="logout-btn"
            onClick={() => setAuth({ token: null, username: null })}
          >
            Sign Out
          </button>
        </div>
      </nav>

      {/* Hero Section */}
      {heroMovie && !searchResults && (
        <section className="hero">
          <div
            className="hero-bg"
            style={{
              backgroundImage: `url(${heroMovie.backdrop_url || heroMovie.poster_url || ""})`,
            }}
          />
          <div className="hero-content">
            <h1 className="hero-title">{heroMovie.title}</h1>
            <div className="hero-meta">
              {heroMovie.vote_average && (
                <span className="hero-rating">
                  ★ {heroMovie.vote_average.toFixed(1)}
                </span>
              )}
              <span className="hero-genres">
                {Array.isArray(heroMovie.genres)
                  ? heroMovie.genres.slice(0, 3).join(" • ")
                  : ""}
              </span>
            </div>
            <p className="hero-overview">{heroMovie.overview}</p>
            <div className="hero-actions">
              <button 
                className="hero-btn primary" 
                onClick={() => window.open(`https://www.google.com/search?q=Where+to+watch+${encodeURIComponent(heroMovie.title)}`, '_blank')}
              >
                ▶ Where to Watch
              </button>
              <button className="hero-btn secondary" onClick={() => setSelected(heroMovie)}>
                ℹ More Info
              </button>
            </div>
          </div>
        </section>
      )}

      {/* Content */}
      <div className="content-section">
        {loading && (
          <div className="page-loading">
            <div className="spinner" />
          </div>
        )}

        {/* Search Results */}
        {searchResults && !loading && (
          <div className="movie-row">
            <div className="row-header">
              <h2 className="row-title">
                Search Results ({searchResults.length})
              </h2>
              <button
                className="logout-btn"
                onClick={() => {
                  setSearchResults(null);
                  setQ("");
                }}
              >
                Clear
              </button>
            </div>
            <div className="row-slider" style={{ flexWrap: "wrap", gap: 12 }}>
              {searchResults.map((m) => (
                <MovieCard
                  key={m.id}
                  movie={m}
                  onClick={() => handleSelectMovie(m)}
                />
              ))}
            </div>
          </div>
        )}

        {/* Genre Rows with My List inserted after Top Rated */}
        {!searchResults &&
          !loading &&
          rows.map((row, index) => (
            <div key={row.title}>
              <MovieRow
                title={row.title}
                movies={row.movies}
                onSelect={handleSelectMovie}
              />
              {/* Insert My List after Top Rated */}
              {index === topRatedIndex && watchlist.length > 0 && (
                <MovieRow
                  title="My List"
                  movies={watchlist}
                  onSelect={handleSelectMovie}
                />
              )}
            </div>
          ))}
      </div>


      {/* Movie Detail Modal */}
      <MovieDetail
        movie={selected}
        onClose={() => setSelected(null)}
        onSelectMovie={handleSelectMovie}
        watchlistIds={watchlistIds}
        onWatchlistChange={fetchWatchlist}
      />
    </>
  );
}

// Movie Row Component with horizontal scroll
function MovieRow({
  title,
  movies,
  onSelect,
}: {
  title: string;
  movies: any[];
  onSelect: (m: any) => void;
}) {
  const sliderRef = useRef<HTMLDivElement>(null);

  const scroll = (direction: "left" | "right") => {
    if (sliderRef.current) {
      const scrollAmount = sliderRef.current.clientWidth * 0.8;
      sliderRef.current.scrollBy({
        left: direction === "left" ? -scrollAmount : scrollAmount,
        behavior: "smooth",
      });
    }
  };

  return (
    <div className="movie-row">
      <div className="row-header">
        <h2 className="row-title">{title}</h2>
      </div>
      <div className="row-slider" ref={sliderRef}>
        {movies.map((m) => (
          <MovieCard key={m.id} movie={m} onClick={() => onSelect(m)} />
        ))}
      </div>
    </div>
  );
}
