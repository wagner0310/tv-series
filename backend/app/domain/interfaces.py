from abc import ABC, abstractmethod
from typing import Optional

from app.domain.entities import (
    AIInsight,
    Comment,
    Episode,
    SearchResult,
    Show,
    WatchedEpisode,
)


class ShowRepository(ABC):
    """Interface for TV show data persistence."""

    @abstractmethod
    async def get_watched_episodes(self, show_id: int) -> list[WatchedEpisode]:
        """Get all watched episodes for a show."""
        pass

    @abstractmethod
    async def mark_episode_watched(self, episode_id: int, show_id: int) -> WatchedEpisode:
        """Mark an episode as watched."""
        pass

    @abstractmethod
    async def unmark_episode_watched(self, episode_id: int, show_id: int) -> bool:
        """Unmark an episode as watched. Returns True if found and deleted."""
        pass

    @abstractmethod
    async def is_episode_watched(self, episode_id: int, show_id: int) -> bool:
        """Check if an episode is marked as watched."""
        pass


class CommentRepository(ABC):
    """Interface for comment data persistence."""

    @abstractmethod
    async def get_comments_for_show(self, show_id: int) -> list[Comment]:
        """Get all comments for a show (including episode comments)."""
        pass

    @abstractmethod
    async def get_comments_for_episode(self, show_id: int, episode_id: int) -> list[Comment]:
        """Get comments for a specific episode."""
        pass

    @abstractmethod
    async def add_comment(self, comment: Comment) -> Comment:
        """Add a new comment."""
        pass

    @abstractmethod
    async def delete_comment(self, comment_id: int) -> bool:
        """Delete a comment. Returns True if found and deleted."""
        pass


class TVShowAPIClient(ABC):
    """Interface for external TV show API (TVMaze)."""

    @abstractmethod
    async def search_shows(self, query: str) -> list[SearchResult]:
        """Search for TV shows by query."""
        pass

    @abstractmethod
    async def get_show(self, show_id: int) -> Optional[Show]:
        """Get show details by ID."""
        pass

    @abstractmethod
    async def get_episodes(self, show_id: int) -> list[Episode]:
        """Get all episodes for a show."""
        pass


class AIInsightGenerator(ABC):
    """Interface for AI insight generation."""

    @abstractmethod
    async def generate_show_insight(
        self,
        show: Show,
        comments: Optional[list[Comment]] = None,
    ) -> AIInsight:
        """Generate an AI insight for a TV show."""
        pass

    @abstractmethod
    async def generate_episode_insight(
        self,
        episode: Episode,
        show: Show,
        comments: Optional[list[Comment]] = None,
    ) -> AIInsight:
        """Generate an AI insight for an episode."""
        pass

