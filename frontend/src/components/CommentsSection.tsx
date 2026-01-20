import { useState, useCallback } from 'react';
import type { Comment } from '../types';

interface CommentsSectionProps {
  comments: Comment[];
  isLoading: boolean;
  onAddComment: (content: string) => Promise<void>;
  onDeleteComment: (commentId: number) => Promise<void>;
  title?: string;
}

export function CommentsSection({
  comments,
  isLoading,
  onAddComment,
  onDeleteComment,
  title = 'Comments',
}: CommentsSectionProps) {
  const [newComment, setNewComment] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();
      if (!newComment.trim() || isSubmitting) return;

      setIsSubmitting(true);
      try {
        await onAddComment(newComment.trim());
        setNewComment('');
      } finally {
        setIsSubmitting(false);
      }
    },
    [newComment, isSubmitting, onAddComment],
  );

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-[var(--color-text-primary)]">
        {title}
      </h3>

      {/* Add comment form */}
      <form onSubmit={handleSubmit} className="space-y-3">
        <textarea
          value={newComment}
          onChange={(e) => setNewComment(e.target.value)}
          placeholder="Share your thoughts..."
          rows={3}
          className="w-full px-4 py-3 bg-[var(--color-bg-tertiary)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)] placeholder:text-[var(--color-text-muted)] focus:outline-none focus:border-[var(--color-accent-primary)] resize-none"
          maxLength={2000}
        />
        <div className="flex items-center justify-between">
          <span className="text-xs text-[var(--color-text-muted)]">
            {newComment.length}/2000
          </span>
          <button
            type="submit"
            disabled={!newComment.trim() || isSubmitting}
            className="px-4 py-2 bg-[var(--color-accent-primary)] text-white rounded-lg font-medium text-sm hover:bg-[var(--color-accent-secondary)] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isSubmitting ? 'Posting...' : 'Post Comment'}
          </button>
        </div>
      </form>

      {/* Comments list */}
      <div className="space-y-3">
        {isLoading ? (
          // Loading skeleton
          Array.from({ length: 3 }).map((_, i) => (
            <div
              key={i}
              className="p-4 rounded-lg bg-[var(--color-bg-card)] border border-[var(--color-border)]"
            >
              <div className="skeleton h-4 w-24 rounded mb-2" />
              <div className="skeleton h-16 w-full rounded" />
            </div>
          ))
        ) : comments.length === 0 ? (
          <p className="text-center py-8 text-[var(--color-text-muted)]">
            No comments yet. Be the first to share your thoughts!
          </p>
        ) : (
          comments.map((comment) => (
            <div
              key={comment.id}
              className="p-4 rounded-lg bg-[var(--color-bg-card)] border border-[var(--color-border)] animate-fade-in"
            >
              <div className="flex items-start justify-between gap-2">
                <span className="text-xs text-[var(--color-text-muted)]">
                  {formatDate(comment.created_at)}
                </span>
                <button
                  onClick={() => onDeleteComment(comment.id)}
                  className="text-[var(--color-text-muted)] hover:text-[var(--color-error)] transition-colors"
                  aria-label="Delete comment"
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
                      d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0"
                    />
                  </svg>
                </button>
              </div>
              <p className="mt-2 text-[var(--color-text-secondary)] whitespace-pre-wrap">
                {comment.content}
              </p>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

