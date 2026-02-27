type FilterValues = {
  genres: string[];
  production_companies: string[];
  runtime_min: string;
  runtime_max: string;
  language: string;
  vote_average_min: string;
  vote_count_min: string;
  popularity_min: string;
};

type Props = {
  open: boolean;
  onClose: () => void;
  value: FilterValues;
  onChange: (v: FilterValues) => void;
  onApply: () => void;
  onReset: () => void;
};

export default function Filters({
  open,
  onClose,
  value,
  onChange,
  onApply,
  onReset,
}: Props) {
  function update(key: keyof FilterValues, val: string) {
    onChange({ ...value, [key]: val });
  }

  return (
    <>
      <div
        className={`filters-backdrop ${open ? "open" : ""}`}
        onClick={onClose}
      />
      <div className={`filters-panel ${open ? "open" : ""}`}>
        <div className="filters-header">
          <h3 className="filters-title">Filters</h3>
          <button className="filters-close" onClick={onClose}>
            ✕
          </button>
        </div>

        <div className="filters-body">
          <div className="filter-group">
            <div className="filter-label">Genre</div>
            <input
              className="filter-input"
              placeholder="e.g. Action, Comedy"
              value={value.genres.join(", ")}
              onChange={(e) =>
                onChange({
                  ...value,
                  genres: e.target.value
                    .split(",")
                    .map((s) => s.trim())
                    .filter(Boolean),
                })
              }
            />
          </div>

          <div className="filter-group">
            <div className="filter-label">Production Company</div>
            <input
              className="filter-input"
              placeholder="e.g. Warner Bros"
              value={value.production_companies.join(", ")}
              onChange={(e) =>
                onChange({
                  ...value,
                  production_companies: e.target.value
                    .split(",")
                    .map((s) => s.trim())
                    .filter(Boolean),
                })
              }
            />
          </div>

          <div className="filter-group">
            <div className="filter-label">Runtime (minutes)</div>
            <div className="filter-row">
              <input
                className="filter-input"
                type="number"
                placeholder="Min"
                value={value.runtime_min}
                onChange={(e) => update("runtime_min", e.target.value)}
              />
              <input
                className="filter-input"
                type="number"
                placeholder="Max"
                value={value.runtime_max}
                onChange={(e) => update("runtime_max", e.target.value)}
              />
            </div>
          </div>

          <div className="filter-group">
            <div className="filter-label">Language</div>
            <input
              className="filter-input"
              placeholder="e.g. en, fr, es"
              value={value.language}
              onChange={(e) => update("language", e.target.value)}
            />
          </div>

          <div className="filter-group">
            <div className="filter-label">Minimum Rating</div>
            <input
              className="filter-input"
              type="number"
              step="0.1"
              min="0"
              max="10"
              placeholder="e.g. 7.0"
              value={value.vote_average_min}
              onChange={(e) => update("vote_average_min", e.target.value)}
            />
          </div>

          <div className="filter-group">
            <div className="filter-label">Minimum Vote Count</div>
            <input
              className="filter-input"
              type="number"
              placeholder="e.g. 100"
              value={value.vote_count_min}
              onChange={(e) => update("vote_count_min", e.target.value)}
            />
          </div>

          <div className="filter-group">
            <div className="filter-label">Minimum Popularity</div>
            <input
              className="filter-input"
              type="number"
              placeholder="e.g. 50"
              value={value.popularity_min}
              onChange={(e) => update("popularity_min", e.target.value)}
            />
          </div>
        </div>

        <div className="filters-footer">
          <button className="filter-btn secondary" onClick={onReset}>
            Reset
          </button>
          <button
            className="filter-btn primary"
            onClick={() => {
              onApply();
              onClose();
            }}
          >
            Apply Filters
          </button>
        </div>
      </div>
    </>
  );
}
