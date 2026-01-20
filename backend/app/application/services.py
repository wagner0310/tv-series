from typing import Optional

from app.domain.entities import AIInsight, Comment, Episode, SearchResult, Show, WatchedEpisode
from app.domain.interfaces import (
    AIInsightGenerator,
    CommentRepository,
    ShowRepository,
    TVShowAPIClient,
)


class ShowService:
    """Service for TV show related operations."""

    def __init__(
        self,
        tv_api: TVShowAPIClient,
        show_repo: ShowRepository,
        comment_repo: CommentRepository,
    ):
        self._tv_api = tv_api
        self._show_repo = show_repo
        self._comment_repo = comment_repo

    async def search_shows(self, query: str) -> list[SearchResult]:
        """Search for TV shows."""
        if not query or len(query.strip()) < 1:
            return []
        return await self._tv_api.search_shows(query.strip())

    async def get_show_details(self, show_id: int) -> Optional[Show]:
        """Get detailed information about a show."""
        return await self._tv_api.get_show(show_id)

    async def get_episodes(self, show_id: int) -> list[Episode]:
        """Get all episodes for a show."""
        return await self._tv_api.get_episodes(show_id)

    async def get_episodes_by_season(self, show_id: int) -> dict[int, list[Episode]]:
        """Get episodes grouped by season."""
        episodes = await self._tv_api.get_episodes(show_id)
        seasons: dict[int, list[Episode]] = {}
        for episode in episodes:
            if episode.season not in seasons:
                seasons[episode.season] = []
            seasons[episode.season].append(episode)
        # Sort episodes within each season
        for season_episodes in seasons.values():
            season_episodes.sort(key=lambda e: e.number)
        return dict(sorted(seasons.items()))


class EpisodeTrackingService:
    """Service for episode watching tracking."""

    def __init__(self, show_repo: ShowRepository):
        self._show_repo = show_repo

    async def get_watched_episodes(self, show_id: int) -> list[WatchedEpisode]:
        """Get all watched episodes for a show."""
        return await self._show_repo.get_watched_episodes(show_id)

    async def mark_watched(self, episode_id: int, show_id: int) -> WatchedEpisode:
        """Mark an episode as watched."""
        return await self._show_repo.mark_episode_watched(episode_id, show_id)

    async def unmark_watched(self, episode_id: int, show_id: int) -> bool:
        """Unmark an episode as watched."""
        return await self._show_repo.unmark_episode_watched(episode_id, show_id)

    async def is_watched(self, episode_id: int, show_id: int) -> bool:
        """Check if an episode is watched."""
        return await self._show_repo.is_episode_watched(episode_id, show_id)


class CommentService:
    """Service for managing comments."""

    def __init__(self, comment_repo: CommentRepository):
        self._comment_repo = comment_repo

    async def get_show_comments(self, show_id: int) -> list[Comment]:
        """Get all comments for a show (excluding episode-specific comments)."""
        all_comments = await self._comment_repo.get_comments_for_show(show_id)
        return [c for c in all_comments if c.episode_id is None]

    async def get_episode_comments(self, show_id: int, episode_id: int) -> list[Comment]:
        """Get comments for a specific episode."""
        return await self._comment_repo.get_comments_for_episode(show_id, episode_id)

    async def get_all_show_comments(self, show_id: int) -> list[Comment]:
        """Get all comments for a show including episode comments."""
        return await self._comment_repo.get_comments_for_show(show_id)

    async def add_comment(
        self,
        content: str,
        show_id: int,
        episode_id: Optional[int] = None,
    ) -> Comment:
        """Add a new comment."""
        comment = Comment(
            id=None,
            content=content,
            show_id=show_id,
            episode_id=episode_id,
        )
        return await self._comment_repo.add_comment(comment)

    async def delete_comment(self, comment_id: int) -> bool:
        """Delete a comment."""
        return await self._comment_repo.delete_comment(comment_id)


class AIInsightService:
    """Service for generating AI insights."""

    def __init__(
        self,
        ai_generator: AIInsightGenerator,
        tv_api: TVShowAPIClient,
        comment_repo: CommentRepository,
    ):
        self._ai_generator = ai_generator
        self._tv_api = tv_api
        self._comment_repo = comment_repo

    async def get_show_insight(
        self,
        show_id: int,
        include_comments: bool = True,
    ) -> Optional[AIInsight]:
        """Generate an AI insight for a show."""
        show = await self._tv_api.get_show(show_id)
        if not show:
            return None

        comments = None
        if include_comments:
            all_comments = await self._comment_repo.get_comments_for_show(show_id)
            comments = [c for c in all_comments if c.episode_id is None]

        return await self._ai_generator.generate_show_insight(show, comments)

    async def get_episode_insight(
        self,
        show_id: int,
        episode_id: int,
        include_comments: bool = True,
    ) -> Optional[AIInsight]:
        """Generate an AI insight for an episode."""
        show = await self._tv_api.get_show(show_id)
        if not show:
            return None

        episodes = await self._tv_api.get_episodes(show_id)
        episode = next((e for e in episodes if e.id == episode_id), None)
        if not episode:
            return None

        comments = None
        if include_comments:
            comments = await self._comment_repo.get_comments_for_episode(show_id, episode_id)

        return await self._ai_generator.generate_episode_insight(episode, show, comments)

