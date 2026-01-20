import { useState, useCallback } from 'react';
import { SearchBar } from '../components/SearchBar';
import { ShowCard } from '../components/ShowCard';
import type { SearchResult } from '../types';
import { searchShows } from '../api/client';

interface SearchPageProps {
  onSelectShow: (showId: number) => void;
}

export function SearchPage({ onSelectShow }: SearchPageProps) {
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = useCallback(async (query: string) => {
    if (!query.trim()) {
      setResults([]);
      setHasSearched(false);
      return;
    }

    setIsLoading(true);
    setError(null);
    setHasSearched(true);

    try {
      const response = await searchShows(query);
      setResults(response.results);
    } catch (err) {
      console.error('Search error:', err);
      setError('Failed to search shows. Please try again.');
      setResults([]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  return (
    <div className="min-h-screen">
      {/* Hero section with search */}
      <section className="relative py-20 px-4">
        {/* Background gradient */}
        <div className="absolute inset-0 bg-linear-gradient(to-b, var(--color-accent-primary)/5, transparent, transparent) pointer-events-none" />

        <div className="relative max-w-4xl mx-auto text-center">
          {/* Logo/Title */}
          <h1 className="text-5xl font-bold mb-4">
            <span className="gradient-text">Series Tracker</span>
          </h1>
          <p className="text-xl text-(--color-text-secondary) mb-10">
            Discover, track, and explore TV series with AI-powered insights
          </p>

          {/* Search bar */}
          <SearchBar onSearch={handleSearch} isLoading={isLoading} />
        </div>
      </section>

      {/* Results section */}
      <section className="px-4 pb-20">
        <div className="max-w-7xl mx-auto">
          {error && (
            <div className="text-center py-8">
              <p className="text-[var(--color-error)]">{error}</p>
            </div>
          )}

          {!error && hasSearched && !isLoading && results.length === 0 && (
            <div className="text-center py-16">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                strokeWidth={1}
                stroke="currentColor"
                className="w-16 h-16 mx-auto text-[var(--color-text-muted)] mb-4"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M15.182 16.318A4.486 4.486 0 0 0 12.016 15a4.486 4.486 0 0 0-3.198 1.318M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0ZM9.75 9.75c0 .414-.168.75-.375.75S9 10.164 9 9.75 9.168 9 9.375 9s.375.336.375.75Zm-.375 0h.008v.015h-.008V9.75Zm5.625 0c0 .414-.168.75-.375.75s-.375-.336-.375-.75.168-.75.375-.75.375.336.375.75Zm-.375 0h.008v.015h-.008V9.75Z"
                />
              </svg>
              <p className="text-[var(--color-text-muted)] text-lg">
                No shows found. Try a different search term.
              </p>
            </div>
          )}

          {results.length > 0 && (
            <>
              <div className="mb-6 flex items-center justify-between">
                <h2 className="text-lg font-medium text-[var(--color-text-secondary)]">
                  Found {results.length} show{results.length !== 1 ? 's' : ''}
                </h2>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
                {results.map((result, index) => (
                  <ShowCard
                    key={result.show.id}
                    show={result.show}
                    onClick={() => onSelectShow(result.show.id)}
                    animationDelay={index * 50}
                  />
                ))}
              </div>
            </>
          )}

          {!hasSearched && (
            <div className="text-center py-16">
              <div className="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-[var(--color-bg-secondary)] border border-[var(--color-border)] mb-6">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  strokeWidth={1.5}
                  stroke="currentColor"
                  className="w-10 h-10 text-[var(--color-accent-primary)]"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M6 20.25h12m-7.5-3v3m3-3v3m-10.125-3h17.25c.621 0 1.125-.504 1.125-1.125V4.875c0-.621-.504-1.125-1.125-1.125H3.375c-.621 0-1.125.504-1.125 1.125v11.25c0 .621.504 1.125 1.125 1.125Z"
                  />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-[var(--color-text-primary)] mb-2">
                Start your journey
              </h3>
              <p className="text-[var(--color-text-muted)] max-w-md mx-auto">
                Search for any TV series to view details, track episodes, leave
                comments, and get AI-powered insights.
              </p>
            </div>
          )}
        </div>
      </section>
    </div>
  );
}

