import { useState, useCallback } from 'react';
import { useDebounce } from '../hooks/useDebounce';
import { useEffect } from 'react';

interface SearchBarProps {
  onSearch: (query: string) => void;
  isLoading?: boolean;
}

export function SearchBar({ onSearch, isLoading = false }: SearchBarProps) {
  const [query, setQuery] = useState('');
  const debouncedQuery = useDebounce(query, 500);

  useEffect(() => {
    if (debouncedQuery.trim()) {
      onSearch(debouncedQuery.trim());
    }
  }, [debouncedQuery, onSearch]);

  const handleClear = useCallback(() => {
    setQuery('');
  }, []);

  return (
    <div className="relative w-full max-w-2xl mx-auto">
      <div className="relative group">
        {/* Search icon */}
        <div className="absolute left-4 top-1/2 -translate-y-1/2 text-[var(--color-text-muted)] transition-colors group-focus-within:text-[var(--color-accent-primary)]">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth={2}
            stroke="currentColor"
            className="w-5 h-5"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z"
            />
          </svg>
        </div>

        {/* Input field */}
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search for TV series..."
          className="w-full py-4 pl-12 pr-12 bg-[var(--color-bg-secondary)] border border-[var(--color-border)] rounded-xl text-[var(--color-text-primary)] placeholder:text-[var(--color-text-muted)] focus:outline-none focus:border-[var(--color-accent-primary)] focus:ring-2 focus:ring-[var(--color-accent-primary)]/20 transition-all"
        />

        {/* Loading spinner or clear button */}
        {(isLoading || query) && (
          <div className="absolute right-4 top-1/2 -translate-y-1/2">
            {isLoading ? (
              <div className="w-5 h-5 border-2 border-[var(--color-accent-primary)] border-t-transparent rounded-full animate-spin" />
            ) : query ? (
              <button
                onClick={handleClear}
                className="text-[var(--color-text-muted)] hover:text-[var(--color-text-primary)] transition-colors p-1"
                aria-label="Clear search"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  strokeWidth={2}
                  stroke="currentColor"
                  className="w-5 h-5"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M6 18 18 6M6 6l12 12"
                  />
                </svg>
              </button>
            ) : null}
          </div>
        )}
      </div>

      {/* Search hint */}
      <p className="mt-3 text-center text-sm text-[var(--color-text-muted)]">
        Try searching for "Breaking Bad", "Game of Thrones", or "The Office"
      </p>
    </div>
  );
}

