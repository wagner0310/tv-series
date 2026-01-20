export interface Show {
  id: number;
  name: string;
  summary: string | null;
  image_url: string | null;
  premiered: string | null;
  genres: string[];
  rating: number | null;
  status: string | null;
  official_site: string | null;
}

export interface SearchResult {
  score: number;
  show: Show;
}

export interface SearchResponse {
  results: SearchResult[];
  query: string;
}

export interface Episode {
  id: number;
  show_id: number;
  name: string;
  season: number;
  number: number;
  summary: string | null;
  airdate: string | null;
  runtime: number | null;
  image_url: string | null;
}

export interface SeasonEpisodes {
  season: number;
  episodes: Episode[];
}

export interface ShowDetail {
  show: Show;
  seasons: SeasonEpisodes[];
}

export interface WatchedEpisode {
  id: number;
  episode_id: number;
  show_id: number;
  watched_at: string;
}

export interface WatchedEpisodesResponse {
  show_id: number;
  episode_ids: number[];
}

export interface Comment {
  id: number;
  content: string;
  show_id: number;
  episode_id: number | null;
  created_at: string;
}

export interface CommentsResponse {
  comments: Comment[];
}

export interface AIInsight {
  content: string;
  show_id: number;
  episode_id: number | null;
  generated_at: string;
}

export interface CreateCommentRequest {
  content: string;
  show_id: number;
  episode_id?: number;
}

export interface MarkWatchedRequest {
  episode_id: number;
  show_id: number;
}

export interface AIInsightRequest {
  show_id: number;
  episode_id?: number;
  include_comments?: boolean;
}

