import type {
  AIInsight,
  AIInsightRequest,
  Comment,
  CommentsResponse,
  CreateCommentRequest,
  MarkWatchedRequest,
  SearchResponse,
  ShowDetail,
  WatchedEpisode,
  WatchedEpisodesResponse,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

class ApiError extends Error {
  public status: number;

  constructor(
    status: number,
    message: string,
  ) {
    super(message);
    this.status = status;
    this.name = 'ApiError';
  }
}

async function fetchApi<T>(
  endpoint: string,
  options: RequestInit = {},
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new ApiError(
      response.status,
      errorData.detail || `HTTP error ${response.status}`,
    );
  }

  // Handle 204 No Content
  if (response.status === 204) {
    return {} as T;
  }

  return response.json();
}

// Search API
export async function searchShows(query: string): Promise<SearchResponse> {
  return fetchApi<SearchResponse>(`/search?q=${encodeURIComponent(query)}`);
}

// Show details API
export async function getShowDetails(showId: number): Promise<ShowDetail> {
  return fetchApi<ShowDetail>(`/shows/${showId}`);
}

// Watched episodes API
export async function getWatchedEpisodes(
  showId: number,
): Promise<WatchedEpisodesResponse> {
  return fetchApi<WatchedEpisodesResponse>(`/shows/${showId}/watched`);
}

export async function markEpisodeWatched(
  request: MarkWatchedRequest,
): Promise<WatchedEpisode> {
  return fetchApi<WatchedEpisode>('/watched', {
    method: 'POST',
    body: JSON.stringify(request),
  });
}

export async function unmarkEpisodeWatched(
  showId: number,
  episodeId: number,
): Promise<void> {
  await fetchApi<void>(`/watched/${showId}/${episodeId}`, {
    method: 'DELETE',
  });
}

// Comments API
export async function getShowComments(
  showId: number,
): Promise<CommentsResponse> {
  return fetchApi<CommentsResponse>(`/shows/${showId}/comments`);
}

export async function getEpisodeComments(
  showId: number,
  episodeId: number,
): Promise<CommentsResponse> {
  return fetchApi<CommentsResponse>(
    `/shows/${showId}/episodes/${episodeId}/comments`,
  );
}

export async function createComment(
  request: CreateCommentRequest,
): Promise<Comment> {
  return fetchApi<Comment>('/comments', {
    method: 'POST',
    body: JSON.stringify(request),
  });
}

export async function deleteComment(commentId: number): Promise<void> {
  await fetchApi<void>(`/comments/${commentId}`, {
    method: 'DELETE',
  });
}

// AI Insights API
export async function generateInsight(
  request: AIInsightRequest,
): Promise<AIInsight> {
  return fetchApi<AIInsight>('/insights', {
    method: 'POST',
    body: JSON.stringify(request),
  });
}

// Health check
export async function healthCheck(): Promise<{ status: string }> {
  return fetchApi<{ status: string }>('/health');
}

