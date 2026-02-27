type SearchMode = "auto" | "title" | "semantic";

type Props = {
  q: string;
  setQ: (v: string) => void;
  mode: SearchMode;
  setMode: (m: SearchMode) => void;
  onSearch: () => void;
};

export default function SearchBar({ q, setQ, mode, setMode, onSearch }: Props) {
  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === "Enter") {
      onSearch();
    }
  }

  return (
    <div className="search-container">
      <input
        className="search-input"
        type="text"
        placeholder="Search movies..."
        value={q}
        onChange={(e) => setQ(e.target.value)}
        onKeyDown={handleKeyDown}
      />
      <div className="search-mode">
        {(["auto", "title", "semantic"] as SearchMode[]).map((m) => (
          <button
            key={m}
            className={mode === m ? "active" : ""}
            onClick={() => setMode(m)}
          >
            {m.charAt(0).toUpperCase() + m.slice(1)}
          </button>
        ))}
      </div>
    </div>
  );
}
