import { useState, useCallback } from 'react';
import type { AIInsight } from '../types';

interface AIInsightPanelProps {
  insight: AIInsight | null;
  isLoading: boolean;
  onGenerateInsight: () => Promise<void>;
  type: 'show' | 'episode';
}

export function AIInsightPanel({
  insight,
  isLoading,
  onGenerateInsight,
  type,
}: AIInsightPanelProps) {
  const [hasGenerated, setHasGenerated] = useState(false);

  const handleGenerate = useCallback(async () => {
    setHasGenerated(true);
    await onGenerateInsight();
  }, [onGenerateInsight]);

  return (
    <div className="rounded-xl border border-[var(--color-accent-primary)]/30 bg-gradient-to-br from-[var(--color-accent-primary)]/5 to-[var(--color-accent-secondary)]/5 overflow-hidden">
      {/* Header */}
      <div className="px-5 py-4 border-b border-[var(--color-accent-primary)]/20 flex items-center gap-3">
        <div className="p-2 rounded-lg bg-[var(--color-accent-primary)]/20">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="currentColor"
            className="w-5 h-5 text-[var(--color-accent-primary)]"
          >
            <path
              fillRule="evenodd"
              d="M9 4.5a.75.75 0 0 1 .721.544l.813 2.846a3.75 3.75 0 0 0 2.576 2.576l2.846.813a.75.75 0 0 1 0 1.442l-2.846.813a3.75 3.75 0 0 0-2.576 2.576l-.813 2.846a.75.75 0 0 1-1.442 0l-.813-2.846a3.75 3.75 0 0 0-2.576-2.576l-2.846-.813a.75.75 0 0 1 0-1.442l2.846-.813A3.75 3.75 0 0 0 7.466 7.89l.813-2.846A.75.75 0 0 1 9 4.5ZM18 1.5a.75.75 0 0 1 .728.568l.258 1.036c.236.94.97 1.674 1.91 1.91l1.036.258a.75.75 0 0 1 0 1.456l-1.036.258c-.94.236-1.674.97-1.91 1.91l-.258 1.036a.75.75 0 0 1-1.456 0l-.258-1.036a2.625 2.625 0 0 0-1.91-1.91l-1.036-.258a.75.75 0 0 1 0-1.456l1.036-.258a2.625 2.625 0 0 0 1.91-1.91l.258-1.036A.75.75 0 0 1 18 1.5ZM16.5 15a.75.75 0 0 1 .712.513l.394 1.183c.15.447.5.799.948.948l1.183.395a.75.75 0 0 1 0 1.422l-1.183.395c-.447.15-.799.5-.948.948l-.395 1.183a.75.75 0 0 1-1.422 0l-.395-1.183a1.5 1.5 0 0 0-.948-.948l-1.183-.395a.75.75 0 0 1 0-1.422l1.183-.395c.447-.15.799-.5.948-.948l.395-1.183A.75.75 0 0 1 16.5 15Z"
              clipRule="evenodd"
            />
          </svg>
        </div>
        <div>
          <h3 className="font-semibold text-[var(--color-text-primary)]">
            AI Insight
          </h3>
          <p className="text-xs text-[var(--color-text-muted)]">
            Powered by AI analysis
          </p>
        </div>
      </div>

      {/* Content */}
      <div className="p-5">
        {!hasGenerated && !insight ? (
          // Initial state - show generate button
          <div className="text-center py-4">
            <p className="text-[var(--color-text-secondary)] mb-4">
              Get AI-powered insights about this {type}, including themes,
              appeal, and recommendations.
            </p>
            <button
              onClick={handleGenerate}
              disabled={isLoading}
              className="inline-flex items-center gap-2 px-5 py-2.5 bg-[var(--color-accent-primary)] text-white rounded-lg font-medium hover:bg-[var(--color-accent-secondary)] disabled:opacity-50 transition-colors"
            >
              {isLoading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 24 24"
                    fill="currentColor"
                    className="w-4 h-4"
                  >
                    <path
                      fillRule="evenodd"
                      d="M9 4.5a.75.75 0 0 1 .721.544l.813 2.846a3.75 3.75 0 0 0 2.576 2.576l2.846.813a.75.75 0 0 1 0 1.442l-2.846.813a3.75 3.75 0 0 0-2.576 2.576l-.813 2.846a.75.75 0 0 1-1.442 0l-.813-2.846a3.75 3.75 0 0 0-2.576-2.576l-2.846-.813a.75.75 0 0 1 0-1.442l2.846-.813A3.75 3.75 0 0 0 7.466 7.89l.813-2.846A.75.75 0 0 1 9 4.5Z"
                      clipRule="evenodd"
                    />
                  </svg>
                  Generate Insight
                </>
              )}
            </button>
          </div>
        ) : isLoading ? (
          // Loading state
          <div className="space-y-3 animate-pulse">
            <div className="skeleton h-4 w-full rounded" />
            <div className="skeleton h-4 w-5/6 rounded" />
            <div className="skeleton h-4 w-4/6 rounded" />
          </div>
        ) : insight ? (
          // Show insight
          <div className="animate-fade-in">
            <p className="text-[var(--color-text-secondary)] leading-relaxed">
              {insight.content}
            </p>
            <div className="mt-4 flex items-center justify-between">
              <span className="text-xs text-[var(--color-text-muted)]">
                Generated{' '}
                {new Date(insight.generated_at).toLocaleDateString('en-US', {
                  month: 'short',
                  day: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit',
                })}
              </span>
              <button
                onClick={handleGenerate}
                disabled={isLoading}
                className="text-xs text-[var(--color-accent-primary)] hover:text-[var(--color-accent-secondary)] transition-colors"
              >
                Regenerate
              </button>
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
}

