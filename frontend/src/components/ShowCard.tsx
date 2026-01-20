import type { Show } from '../types';

interface ShowCardProps {
  show: Show;
  onClick: () => void;
  animationDelay?: number;
}

export function ShowCard({ show, onClick, animationDelay = 0 }: ShowCardProps) {
  const year = show.premiered ? new Date(show.premiered).getFullYear() : null;

  return (
    <article
      onClick={onClick}
      className="group cursor-pointer animate-slide-up opacity-0"
      style={{
        animationDelay: `${animationDelay}ms`,
        animationFillMode: 'forwards',
      }}
    >
      <div className="relative overflow-hidden rounded-xl bg-[var(--color-bg-card)] border border-[var(--color-border)] transition-all duration-300 hover:border-[var(--color-accent-primary)]/50 hover:shadow-lg hover:shadow-[var(--color-accent-primary)]/10 hover:-translate-y-1">
        {/* Poster image */}
        <div className="aspect-[2/3] relative overflow-hidden bg-[var(--color-bg-tertiary)]">
          {show.image_url ? (
            <img
              src={show.image_url}
              alt={`${show.name} poster`}
              className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
              loading="lazy"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center text-[var(--color-text-muted)]">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                strokeWidth={1}
                stroke="currentColor"
                className="w-16 h-16"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M6 20.25h12m-7.5-3v3m3-3v3m-10.125-3h17.25c.621 0 1.125-.504 1.125-1.125V4.875c0-.621-.504-1.125-1.125-1.125H3.375c-.621 0-1.125.504-1.125 1.125v11.25c0 .621.504 1.125 1.125 1.125Z"
                />
              </svg>
            </div>
          )}

          {/* Rating badge */}
          {show.rating && (
            <div className="absolute top-3 right-3 px-2 py-1 rounded-md bg-black/60 backdrop-blur-sm text-sm font-medium flex items-center gap-1">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill="currentColor"
                className="w-4 h-4 text-yellow-400"
              >
                <path
                  fillRule="evenodd"
                  d="M10.788 3.21c.448-1.077 1.976-1.077 2.424 0l2.082 5.006 5.404.434c1.164.093 1.636 1.545.749 2.305l-4.117 3.527 1.257 5.273c.271 1.136-.964 2.033-1.96 1.425L12 18.354 7.373 21.18c-.996.608-2.231-.29-1.96-1.425l1.257-5.273-4.117-3.527c-.887-.76-.415-2.212.749-2.305l5.404-.434 2.082-5.005Z"
                  clipRule="evenodd"
                />
              </svg>
              <span>{show.rating.toFixed(1)}</span>
            </div>
          )}
        </div>

        {/* Content */}
        <div className="p-4">
          <h3 className="font-semibold text-lg text-[var(--color-text-primary)] line-clamp-1 group-hover:text-[var(--color-accent-primary)] transition-colors">
            {show.name}
          </h3>

          <div className="mt-2 flex items-center gap-2 text-sm text-[var(--color-text-secondary)]">
            {year && <span>{year}</span>}
            {year && show.status && <span>•</span>}
            {show.status && (
              <span
                className={
                  show.status === 'Running'
                    ? 'text-[var(--color-success)]'
                    : 'text-[var(--color-text-muted)]'
                }
              >
                {show.status}
              </span>
            )}
          </div>

          {/* Genres */}
          {show.genres.length > 0 && (
            <div className="mt-3 flex flex-wrap gap-1.5">
              {show.genres.slice(0, 3).map((genre) => (
                <span
                  key={genre}
                  className="px-2 py-0.5 text-xs rounded-full bg-[var(--color-bg-tertiary)] text-[var(--color-text-muted)]"
                >
                  {genre}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>
    </article>
  );
}

