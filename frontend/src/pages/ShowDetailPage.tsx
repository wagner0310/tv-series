import { useState, useEffect, useCallback } from 'react';
import { EpisodeCard } from '../components/EpisodeCard';
import { CommentsSection } from '../components/CommentsSection';
import { AIInsightPanel } from '../components/AIInsightPanel';
import { Modal } from '../components/Modal';
import { LoadingSpinner } from '../components/LoadingSpinner';
import type { ShowDetail, Comment, AIInsight, Episode } from '../types';
import {
  getShowDetails,
  getWatchedEpisodes,
  markEpisodeWatched,
  unmarkEpisodeWatched,
  getShowComments,
  getEpisodeComments,
  createComment,
  deleteComment,
  generateInsight,
} from '../api/client';

interface ShowDetailPageProps {
  showId: number;
  onBack: () => void;
}

export function ShowDetailPage({ showId, onBack }: ShowDetailPageProps) {
  const [showData, setShowData] = useState<ShowDetail | null>(null);
  const [watchedEpisodes, setWatchedEpisodes] = useState<Set<number>>(
    new Set(),
  );
  const [showComments, setShowComments] = useState<Comment[]>([]);
  const [showInsight, setShowInsight] = useState<AIInsight | null>(null);
  const [selectedSeason, setSelectedSeason] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingComments, setIsLoadingComments] = useState(false);
  const [isLoadingInsight, setIsLoadingInsight] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Episode comments modal state
  const [selectedEpisode, setSelectedEpisode] = useState<Episode | null>(null);
  const [episodeComments, setEpisodeComments] = useState<Comment[]>([]);
  const [episodeInsight, setEpisodeInsight] = useState<AIInsight | null>(null);
  const [isLoadingEpisodeComments, setIsLoadingEpisodeComments] =
    useState(false);
  const [isLoadingEpisodeInsight, setIsLoadingEpisodeInsight] = useState(false);

  // Load show data
  useEffect(() => {
    async function loadShowData() {
      setIsLoading(true);
      setError(null);

      try {
        const [details, watched, comments] = await Promise.all([
          getShowDetails(showId),
          getWatchedEpisodes(showId),
          getShowComments(showId),
        ]);

        setShowData(details);
        setWatchedEpisodes(new Set(watched.episode_ids));
        setShowComments(comments.comments);

        // Set default selected season
        if (details.seasons.length > 0) {
          setSelectedSeason(details.seasons[0].season);
        }
      } catch (err) {
        console.error('Failed to load show data:', err);
        setError('Failed to load show details. Please try again.');
      } finally {
        setIsLoading(false);
      }
    }

    loadShowData();
  }, [showId]);

  // Toggle watched status
  const handleToggleWatched = useCallback(
    async (episodeId: number) => {
      const isCurrentlyWatched = watchedEpisodes.has(episodeId);

      // Optimistic update
      setWatchedEpisodes((prev) => {
        const next = new Set(prev);
        if (isCurrentlyWatched) {
          next.delete(episodeId);
        } else {
          next.add(episodeId);
        }
        return next;
      });

      try {
        if (isCurrentlyWatched) {
          await unmarkEpisodeWatched(showId, episodeId);
        } else {
          await markEpisodeWatched({ episode_id: episodeId, show_id: showId });
        }
      } catch (err) {
        // Revert on error
        console.error('Failed to update watched status:', err);
        setWatchedEpisodes((prev) => {
          const next = new Set(prev);
          if (isCurrentlyWatched) {
            next.add(episodeId);
          } else {
            next.delete(episodeId);
          }
          return next;
        });
      }
    },
    [showId, watchedEpisodes],
  );

  // Show comments handlers
  const handleAddShowComment = useCallback(
    async (content: string) => {
      const comment = await createComment({
        content,
        show_id: showId,
      });
      setShowComments((prev) => [comment, ...prev]);
    },
    [showId],
  );

  const handleDeleteShowComment = useCallback(async (commentId: number) => {
    await deleteComment(commentId);
    setShowComments((prev) => prev.filter((c) => c.id !== commentId));
  }, []);

  // Generate show insight
  const handleGenerateShowInsight = useCallback(async () => {
    setIsLoadingInsight(true);
    try {
      const insight = await generateInsight({
        show_id: showId,
        include_comments: true,
      });
      setShowInsight(insight);
    } catch (err) {
      console.error('Failed to generate insight:', err);
    } finally {
      setIsLoadingInsight(false);
    }
  }, [showId]);

  // Open episode comments modal
  const handleViewEpisodeComments = useCallback(
    async (episode: Episode) => {
      setSelectedEpisode(episode);
      setIsLoadingEpisodeComments(true);
      setEpisodeInsight(null);

      try {
        const comments = await getEpisodeComments(showId, episode.id);
        setEpisodeComments(comments.comments);
      } catch (err) {
        console.error('Failed to load episode comments:', err);
        setEpisodeComments([]);
      } finally {
        setIsLoadingEpisodeComments(false);
      }
    },
    [showId],
  );

  // Episode comments handlers
  const handleAddEpisodeComment = useCallback(
    async (content: string) => {
      if (!selectedEpisode) return;
      const comment = await createComment({
        content,
        show_id: showId,
        episode_id: selectedEpisode.id,
      });
      setEpisodeComments((prev) => [comment, ...prev]);
    },
    [showId, selectedEpisode],
  );

  const handleDeleteEpisodeComment = useCallback(async (commentId: number) => {
    await deleteComment(commentId);
    setEpisodeComments((prev) => prev.filter((c) => c.id !== commentId));
  }, []);

  // Generate episode insight
  const handleGenerateEpisodeInsight = useCallback(async () => {
    if (!selectedEpisode) return;
    setIsLoadingEpisodeInsight(true);
    try {
      const insight = await generateInsight({
        show_id: showId,
        episode_id: selectedEpisode.id,
        include_comments: true,
      });
      setEpisodeInsight(insight);
    } catch (err) {
      console.error('Failed to generate episode insight:', err);
    } finally {
      setIsLoadingEpisodeInsight(false);
    }
  }, [showId, selectedEpisode]);

  // Close episode modal
  const handleCloseEpisodeModal = useCallback(() => {
    setSelectedEpisode(null);
    setEpisodeComments([]);
    setEpisodeInsight(null);
  }, []);

  // Strip HTML from summary
  const cleanSummary = showData?.show.summary
    ? showData.show.summary.replace(/<[^>]*>/g, '')
    : null;

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (error || !showData) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-[var(--color-error)] mb-4">
            {error || 'Show not found'}
          </p>
          <button
            onClick={onBack}
            className="px-4 py-2 bg-[var(--color-accent-primary)] text-white rounded-lg"
          >
            Go Back
          </button>
        </div>
      </div>
    );
  }

  const { show, seasons } = showData;
  const currentSeason = seasons.find((s) => s.season === selectedSeason);
  const totalEpisodes = seasons.reduce(
    (sum, s) => sum + s.episodes.length,
    0,
  );
  const watchedCount = watchedEpisodes.size;

  return (
    <div className="min-h-screen">
      {/* Header with back button */}
      <header className="sticky top-0 z-40 bg-[var(--color-bg-primary)]/80 backdrop-blur-md border-b border-[var(--color-border)]">
        <div className="max-w-7xl mx-auto px-4 py-3 flex items-center gap-4">
          <button
            onClick={onBack}
            className="p-2 rounded-lg hover:bg-[var(--color-bg-secondary)] text-[var(--color-text-muted)] hover:text-[var(--color-text-primary)] transition-colors"
            aria-label="Go back"
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
                d="M10.5 19.5 3 12m0 0 7.5-7.5M3 12h18"
              />
            </svg>
          </button>
          <h1 className="font-semibold text-[var(--color-text-primary)] truncate">
            {show.name}
          </h1>
        </div>
      </header>

      {/* Hero section */}
      <section className="relative">
        {/* Background image */}
        {show.image_url && (
          <div className="absolute inset-0 h-80 overflow-hidden">
            <img
              src={show.image_url}
              alt=""
              className="w-full h-full object-cover opacity-20 blur-xl scale-110"
            />
            <div className="absolute inset-0 bg-gradient-to-b from-transparent via-[var(--color-bg-primary)]/50 to-[var(--color-bg-primary)]" />
          </div>
        )}

        <div className="relative max-w-7xl mx-auto px-4 py-8">
          <div className="flex flex-col md:flex-row gap-8">
            {/* Poster */}
            <div className="flex-shrink-0 w-48 mx-auto md:mx-0">
              <div className="aspect-[2/3] rounded-xl overflow-hidden bg-[var(--color-bg-secondary)] shadow-2xl">
                {show.image_url ? (
                  <img
                    src={show.image_url}
                    alt={`${show.name} poster`}
                    className="w-full h-full object-cover"
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
              </div>
            </div>

            {/* Info */}
            <div className="flex-1 min-w-0">
              <h2 className="text-3xl font-bold text-[var(--color-text-primary)]">
                {show.name}
              </h2>

              <div className="mt-3 flex flex-wrap items-center gap-3 text-sm">
                {show.premiered && (
                  <span className="text-[var(--color-text-secondary)]">
                    {new Date(show.premiered).getFullYear()}
                  </span>
                )}
                {show.rating && (
                  <span className="flex items-center gap-1 text-yellow-400">
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      viewBox="0 0 24 24"
                      fill="currentColor"
                      className="w-4 h-4"
                    >
                      <path
                        fillRule="evenodd"
                        d="M10.788 3.21c.448-1.077 1.976-1.077 2.424 0l2.082 5.006 5.404.434c1.164.093 1.636 1.545.749 2.305l-4.117 3.527 1.257 5.273c.271 1.136-.964 2.033-1.96 1.425L12 18.354 7.373 21.18c-.996.608-2.231-.29-1.96-1.425l1.257-5.273-4.117-3.527c-.887-.76-.415-2.212.749-2.305l5.404-.434 2.082-5.005Z"
                        clipRule="evenodd"
                      />
                    </svg>
                    {show.rating.toFixed(1)}
                  </span>
                )}
                {show.status && (
                  <span
                    className={`px-2 py-0.5 rounded-full text-xs ${
                      show.status === 'Running'
                        ? 'bg-[var(--color-success)]/20 text-[var(--color-success)]'
                        : 'bg-[var(--color-bg-tertiary)] text-[var(--color-text-muted)]'
                    }`}
                  >
                    {show.status}
                  </span>
                )}
              </div>

              {/* Genres */}
              {show.genres.length > 0 && (
                <div className="mt-4 flex flex-wrap gap-2">
                  {show.genres.map((genre) => (
                    <span
                      key={genre}
                      className="px-3 py-1 text-sm rounded-full bg-[var(--color-bg-secondary)] border border-[var(--color-border)] text-[var(--color-text-secondary)]"
                    >
                      {genre}
                    </span>
                  ))}
                </div>
              )}

              {/* Summary */}
              {cleanSummary && (
                <p className="mt-4 text-[var(--color-text-secondary)] line-clamp-4">
                  {cleanSummary}
                </p>
              )}

              {/* Progress */}
              <div className="mt-6 p-4 rounded-lg bg-[var(--color-bg-secondary)] border border-[var(--color-border)]">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-[var(--color-text-muted)]">
                    Watch Progress
                  </span>
                  <span className="text-sm font-medium text-[var(--color-text-primary)]">
                    {watchedCount}/{totalEpisodes} episodes
                  </span>
                </div>
                <div className="h-2 bg-[var(--color-bg-tertiary)] rounded-full overflow-hidden">
                  <div
                    className="h-full bg-[var(--color-accent-primary)] rounded-full transition-all duration-300"
                    style={{
                      width: `${totalEpisodes > 0 ? (watchedCount / totalEpisodes) * 100 : 0}%`,
                    }}
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Content */}
      <section className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Episodes - 2 columns */}
          <div className="lg:col-span-2 space-y-6">
            <div className="flex items-center justify-between">
              <h3 className="text-xl font-semibold text-[var(--color-text-primary)]">
                Episodes
              </h3>
            </div>

            {/* Season tabs */}
            {seasons.length > 0 && (
              <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-thin">
                {seasons.map((season) => (
                  <button
                    key={season.season}
                    onClick={() => setSelectedSeason(season.season)}
                    className={`flex-shrink-0 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                      selectedSeason === season.season
                        ? 'bg-[var(--color-accent-primary)] text-white'
                        : 'bg-[var(--color-bg-secondary)] text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]'
                    }`}
                  >
                    Season {season.season}
                  </button>
                ))}
              </div>
            )}

            {/* Episode list */}
            {currentSeason && (
              <div className="space-y-3">
                {currentSeason.episodes.map((episode) => (
                  <EpisodeCard
                    key={episode.id}
                    episode={episode}
                    isWatched={watchedEpisodes.has(episode.id)}
                    onToggleWatched={() => handleToggleWatched(episode.id)}
                    onViewComments={() => handleViewEpisodeComments(episode)}
                  />
                ))}
              </div>
            )}
          </div>

          {/* Sidebar - 1 column */}
          <div className="space-y-6">
            {/* AI Insight */}
            <AIInsightPanel
              insight={showInsight}
              isLoading={isLoadingInsight}
              onGenerateInsight={handleGenerateShowInsight}
              type="show"
            />

            {/* Comments */}
            <div className="p-5 rounded-xl bg-[var(--color-bg-secondary)] border border-[var(--color-border)]">
              <CommentsSection
                comments={showComments}
                isLoading={isLoadingComments}
                onAddComment={handleAddShowComment}
                onDeleteComment={handleDeleteShowComment}
                title="Series Comments"
              />
            </div>
          </div>
        </div>
      </section>

      {/* Episode Comments Modal */}
      <Modal
        isOpen={!!selectedEpisode}
        onClose={handleCloseEpisodeModal}
        title={
          selectedEpisode
            ? `S${selectedEpisode.season}E${selectedEpisode.number} - ${selectedEpisode.name}`
            : ''
        }
      >
        {selectedEpisode && (
          <div className="space-y-6">
            {/* Episode AI Insight */}
            <AIInsightPanel
              insight={episodeInsight}
              isLoading={isLoadingEpisodeInsight}
              onGenerateInsight={handleGenerateEpisodeInsight}
              type="episode"
            />

            {/* Episode Comments */}
            <CommentsSection
              comments={episodeComments}
              isLoading={isLoadingEpisodeComments}
              onAddComment={handleAddEpisodeComment}
              onDeleteComment={handleDeleteEpisodeComment}
              title="Episode Comments"
            />
          </div>
        )}
      </Modal>
    </div>
  );
}

