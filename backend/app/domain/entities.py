from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Show:
    """Represents a TV show."""
    id: int
    name: str
    summary: Optional[str] = None
    image_url: Optional[str] = None
    premiered: Optional[str] = None
    genres: list[str] = field(default_factory=list)
    rating: Optional[float] = None
    status: Optional[str] = None
    official_site: Optional[str] = None


@dataclass
class Episode:
    """Represents a TV show episode."""
    id: int
    show_id: int
    name: str
    season: int
    number: int
    summary: Optional[str] = None
    airdate: Optional[str] = None
    runtime: Optional[int] = None
    image_url: Optional[str] = None


@dataclass
class WatchedEpisode:
    """Represents a user's watched episode record."""
    id: Optional[int]
    episode_id: int
    show_id: int
    watched_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Comment:
    """Represents a user comment on a show or episode."""
    id: Optional[int]
    content: str
    show_id: int
    episode_id: Optional[int] = None  # None means comment is on the show itself
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AIInsight:
    """Represents an AI-generated insight."""
    content: str
    show_id: int
    episode_id: Optional[int] = None
    generated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SearchResult:
    """Represents a search result from TVMaze."""
    score: float
    show: Show

