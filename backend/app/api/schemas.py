from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# Show schemas
class ShowSchema(BaseModel):
    """Schema for TV show."""
    id: int
    name: str
    summary: Optional[str] = None
    image_url: Optional[str] = None
    premiered: Optional[str] = None
    genres: list[str] = Field(default_factory=list)
    rating: Optional[float] = None
    status: Optional[str] = None
    official_site: Optional[str] = None


class SearchResultSchema(BaseModel):
    """Schema for search result."""
    score: float
    show: ShowSchema


class SearchResponseSchema(BaseModel):
    """Schema for search response."""
    results: list[SearchResultSchema]
    query: str


# Episode schemas
class EpisodeSchema(BaseModel):
    """Schema for episode."""
    id: int
    show_id: int
    name: str
    season: int
    number: int
    summary: Optional[str] = None
    airdate: Optional[str] = None
    runtime: Optional[int] = None
    image_url: Optional[str] = None


class SeasonEpisodesSchema(BaseModel):
    """Schema for episodes grouped by season."""
    season: int
    episodes: list[EpisodeSchema]


class ShowDetailSchema(BaseModel):
    """Schema for detailed show information with seasons."""
    show: ShowSchema
    seasons: list[SeasonEpisodesSchema]


# Watched episode schemas
class WatchedEpisodeSchema(BaseModel):
    """Schema for watched episode record."""
    id: int
    episode_id: int
    show_id: int
    watched_at: datetime


class MarkWatchedRequest(BaseModel):
    """Request schema for marking episode as watched."""
    episode_id: int
    show_id: int


class WatchedEpisodesResponse(BaseModel):
    """Response schema for watched episodes."""
    show_id: int
    episode_ids: list[int]


# Comment schemas
class CommentSchema(BaseModel):
    """Schema for comment."""
    id: int
    content: str
    show_id: int
    episode_id: Optional[int] = None
    created_at: datetime


class CreateCommentRequest(BaseModel):
    """Request schema for creating a comment."""
    content: str = Field(..., min_length=1, max_length=2000)
    show_id: int
    episode_id: Optional[int] = None


class CommentsResponse(BaseModel):
    """Response schema for comments list."""
    comments: list[CommentSchema]


# AI Insight schemas
class AIInsightSchema(BaseModel):
    """Schema for AI insight."""
    content: str
    show_id: int
    episode_id: Optional[int] = None
    generated_at: datetime


class AIInsightRequest(BaseModel):
    """Request schema for generating AI insight."""
    show_id: int
    episode_id: Optional[int] = None
    include_comments: bool = True

