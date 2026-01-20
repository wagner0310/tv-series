import type { Episode } from '../types';

interface EpisodeCardProps {
  episode: Episode;
  isWatched: boolean;
  onToggleWatched: () => void;
  onViewComments: () => void;
  commentCount?: number;
}

export function EpisodeCard({
  episode,
  isWatched,
  onToggleWatched,
  onViewComments,
  commentCount = 0,
}: EpisodeCardProps) {
  // Strip HTML tags from summary
  const cleanSummary = episode.summary
    ? episode.summary.replace(/<[^>]*>/g, '')
    : null;

  return (
    <div
      className={`group relative p-4 rounded-lg border transition-all duration-200 ${
        isWatched
          ? 'bg-[var(--color-accent-primary)]/5 border-[var(--color-accent-primary)]/30'
          : 'bg-[var(--color-bg-card)] border-[var(--color-border)] hover:border-[var(--color-border)]/80'
      }`}
    >
      <div className="flex gap-4">
        {/* Episode image */}
        <div className="flex-shrink-0 w-28 h-16 rounded-md overflow-hidden bg-[var(--color-bg-tertiary)]">
          {episode.image_url ? (
            <img
              src={episode.image_url}
              alt={episode.name}
              className="w-full h-full object-cover"
              loading="lazy"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center text-[var(--color-text-muted)]">
              <span className="text-xs font-mono">
                S{episode.season}E{episode.number}
              </span>
            </div>
          )}
        </div>

        {/* Episode info */}
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            <div className="min-w-0">
              <div className="flex items-center gap-2">
                <span className="text-xs font-mono text-[var(--color-accent-primary)]">
                  E{episode.number.toString().padStart(2, '0')}
                </span>
                <h4 className="font-medium text-[var(--color-text-primary)] truncate">
                  {episode.name}
                </h4>
              </div>

              {episode.airdate && (
                <p className="mt-0.5 text-xs text-[var(--color-text-muted)]">
                  {new Date(episode.airdate).toLocaleDateString('en-US', {
                    year: 'numeric',
                    month: 'short',
                    day: 'numeric',
                  })}
                  {episode.runtime && ` • ${episode.runtime} min`}
                </p>
              )}
            </div>

            {/* Watched toggle */}
            <button
              onClick={(e) => {
                e.stopPropagation();
                onToggleWatched();
              }}
              className={`flex-shrink-0 p-2 rounded-full transition-all ${
                isWatched
                  ? 'bg-[var(--color-accent-primary)] text-white'
                  : 'bg-[var(--color-bg-tertiary)] text-[var(--color-text-muted)] hover:text-[var(--color-accent-primary)]'
              }`}
              aria-label={isWatched ? 'Mark as unwatched' : 'Mark as watched'}
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill="currentColor"
                className="w-4 h-4"
              >
                <path
                  fillRule="evenodd"
                  d="M19.916 4.626a.75.75 0 0 1 .208 1.04l-9 13.5a.75.75 0 0 1-1.154.114l-6-6a.75.75 0 0 1 1.06-1.06l5.353 5.353 8.493-12.74a.75.75 0 0 1 1.04-.207Z"
                  clipRule="evenodd"
                />
              </svg>
            </button>
          </div>

          {/* Summary */}
          {cleanSummary && (
            <p className="mt-2 text-sm text-[var(--color-text-secondary)] line-clamp-2">
              {cleanSummary}
            </p>
          )}

          {/* Comments button */}
          <button
            onClick={(e) => {
              e.stopPropagation();
              onViewComments();
            }}
            className="mt-2 inline-flex items-center gap-1.5 text-xs text-[var(--color-text-muted)] hover:text-[var(--color-accent-primary)] transition-colors"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={1.5}
              stroke="currentColor"
              className="w-4 h-4"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M8.625 12a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm0 0H8.25m4.125 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm0 0H12m4.125 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm0 0h-.375M21 12c0 4.556-4.03 8.25-9 8.25a9.764 9.764 0 0 1-2.555-.337A5.972 5.972 0 0 1 5.41 20.97a5.969 5.969 0 0 1-.474-.065 4.48 4.48 0 0 0 .978-2.025c.09-.457-.133-.901-.467-1.226C3.93 16.178 3 14.189 3 12c0-4.556 4.03-8.25 9-8.25s9 3.694 9 8.25Z"
              />
            </svg>
            {commentCount > 0 ? `${commentCount} comments` : 'Add comment'}
          </button>
        </div>
      </div>
    </div>
  );
}

