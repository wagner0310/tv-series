interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export function LoadingSpinner({
  size = 'md',
  className = '',
}: LoadingSpinnerProps) {
  const sizeClasses = {
    sm: 'w-4 h-4 border-2',
    md: 'w-8 h-8 border-3',
    lg: 'w-12 h-12 border-4',
  };

  return (
    <div
      className={`${sizeClasses[size]} border-[var(--color-accent-primary)] border-t-transparent rounded-full animate-spin ${className}`}
    />
  );
}

export function LoadingScreen() {
  return (
    <div className="fixed inset-0 flex items-center justify-center bg-[var(--color-bg-primary)]">
      <div className="text-center">
        <LoadingSpinner size="lg" />
        <p className="mt-4 text-[var(--color-text-muted)]">Loading...</p>
      </div>
    </div>
  );
}

export function LoadingOverlay() {
  return (
    <div className="absolute inset-0 flex items-center justify-center bg-[var(--color-bg-primary)]/80 backdrop-blur-sm">
      <LoadingSpinner size="lg" />
    </div>
  );
}

