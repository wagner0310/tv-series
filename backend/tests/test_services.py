"""Tests for application services."""
from datetime import datetime
from typing import Optional
from unittest.mock import AsyncMock

import pytest

from app.application.services import (
    AIInsightService,
    CommentService,
    EpisodeTrackingService,
    ShowService,
)
from app.domain.entities import (
    AIInsight,
    Comment,
    Episode,
    SearchResult,
    Show,
    WatchedEpisode,
)
from app.domain.interfaces import (
    AIInsightGenerator,
    CommentRepository,
    ShowRepository,
    TVShowAPIClient,
)


# Mock implementations
class MockTVShowAPIClient(TVShowAPIClient):
    """Mock TV show API client for testing."""

    def __init__(self):
        self.shows: dict[int, Show] = {}
        self.episodes: dict[int, list[Episode]] = {}

    async def search_shows(self, query: str) -> list[SearchResult]:
        results = []
        for show in self.shows.values():
            if query.lower() in show.name.lower():
                results.append(SearchResult(score=1.0, show=show))
        return results

    async def get_show(self, show_id: int) -> Optional[Show]:
        return self.shows.get(show_id)

    async def get_episodes(self, show_id: int) -> list[Episode]:
        return self.episodes.get(show_id, [])


class MockShowRepository(ShowRepository):
    """Mock show repository for testing."""

    def __init__(self):
        self.watched: dict[tuple[int, int], WatchedEpisode] = {}
        self._id_counter = 1

    async def get_watched_episodes(self, show_id: int) -> list[WatchedEpisode]:
        return [w for (sid, _), w in self.watched.items() if sid == show_id]

    async def mark_episode_watched(self, episode_id: int, show_id: int) -> WatchedEpisode:
        key = (show_id, episode_id)
        if key not in self.watched:
            self.watched[key] = WatchedEpisode(
                id=self._id_counter,
                episode_id=episode_id,
                show_id=show_id,
            )
            self._id_counter += 1
        return self.watched[key]

    async def unmark_episode_watched(self, episode_id: int, show_id: int) -> bool:
        key = (show_id, episode_id)
        if key in self.watched:
            del self.watched[key]
            return True
        return False

    async def is_episode_watched(self, episode_id: int, show_id: int) -> bool:
        return (show_id, episode_id) in self.watched


class MockCommentRepository(CommentRepository):
    """Mock comment repository for testing."""

    def __init__(self):
        self.comments: list[Comment] = []
        self._id_counter = 1

    async def get_comments_for_show(self, show_id: int) -> list[Comment]:
        return [c for c in self.comments if c.show_id == show_id]

    async def get_comments_for_episode(self, show_id: int, episode_id: int) -> list[Comment]:
        return [
            c
            for c in self.comments
            if c.show_id == show_id and c.episode_id == episode_id
        ]

    async def add_comment(self, comment: Comment) -> Comment:
        new_comment = Comment(
            id=self._id_counter,
            content=comment.content,
            show_id=comment.show_id,
            episode_id=comment.episode_id,
            created_at=comment.created_at,
        )
        self.comments.append(new_comment)
        self._id_counter += 1
        return new_comment

    async def delete_comment(self, comment_id: int) -> bool:
        for i, c in enumerate(self.comments):
            if c.id == comment_id:
                del self.comments[i]
                return True
        return False


class MockAIInsightGenerator(AIInsightGenerator):
    """Mock AI insight generator for testing."""

    async def generate_show_insight(
        self,
        show: Show,
        comments: Optional[list[Comment]] = None,
    ) -> AIInsight:
        return AIInsight(
            content=f"Mock insight for {show.name}",
            show_id=show.id,
        )

    async def generate_episode_insight(
        self,
        episode: Episode,
        show: Show,
        comments: Optional[list[Comment]] = None,
    ) -> AIInsight:
        return AIInsight(
            content=f"Mock insight for {episode.name}",
            show_id=show.id,
            episode_id=episode.id,
        )


class TestShowService:
    """Tests for ShowService."""

    @pytest.fixture
    def mock_api(self):
        api = MockTVShowAPIClient()
        api.shows[1] = Show(
            id=1,
            name="Breaking Bad",
            genres=["Drama", "Crime"],
        )
        api.shows[2] = Show(
            id=2,
            name="Better Call Saul",
            genres=["Drama"],
        )
        api.episodes[1] = [
            Episode(id=101, show_id=1, name="Pilot", season=1, number=1),
            Episode(id=102, show_id=1, name="Cat's in the Bag", season=1, number=2),
            Episode(id=201, show_id=1, name="Seven Thirty-Seven", season=2, number=1),
        ]
        return api

    @pytest.fixture
    def service(self, mock_api):
        return ShowService(
            tv_api=mock_api,
            show_repo=MockShowRepository(),
            comment_repo=MockCommentRepository(),
        )

    @pytest.mark.asyncio
    async def test_search_shows(self, service):
        """Test searching for shows."""
        results = await service.search_shows("Breaking")
        assert len(results) == 1
        assert results[0].show.name == "Breaking Bad"

    @pytest.mark.asyncio
    async def test_search_shows_empty_query(self, service):
        """Test searching with empty query."""
        results = await service.search_shows("")
        assert results == []

    @pytest.mark.asyncio
    async def test_get_show_details(self, service):
        """Test getting show details."""
        show = await service.get_show_details(1)
        assert show is not None
        assert show.name == "Breaking Bad"

    @pytest.mark.asyncio
    async def test_get_show_details_not_found(self, service):
        """Test getting non-existent show."""
        show = await service.get_show_details(999)
        assert show is None

    @pytest.mark.asyncio
    async def test_get_episodes_by_season(self, service):
        """Test getting episodes grouped by season."""
        seasons = await service.get_episodes_by_season(1)
        assert 1 in seasons
        assert 2 in seasons
        assert len(seasons[1]) == 2  # Season 1 has 2 episodes
        assert len(seasons[2]) == 1  # Season 2 has 1 episode


class TestEpisodeTrackingService:
    """Tests for EpisodeTrackingService."""

    @pytest.fixture
    def service(self):
        return EpisodeTrackingService(MockShowRepository())

    @pytest.mark.asyncio
    async def test_mark_watched(self, service):
        """Test marking an episode as watched."""
        watched = await service.mark_watched(episode_id=101, show_id=1)
        assert watched.episode_id == 101
        assert watched.show_id == 1

    @pytest.mark.asyncio
    async def test_unmark_watched(self, service):
        """Test unmarking an episode as watched."""
        await service.mark_watched(episode_id=101, show_id=1)
        result = await service.unmark_watched(episode_id=101, show_id=1)
        assert result is True

    @pytest.mark.asyncio
    async def test_unmark_not_watched(self, service):
        """Test unmarking an episode that wasn't watched."""
        result = await service.unmark_watched(episode_id=999, show_id=1)
        assert result is False

    @pytest.mark.asyncio
    async def test_is_watched(self, service):
        """Test checking if episode is watched."""
        assert await service.is_watched(101, 1) is False
        await service.mark_watched(101, 1)
        assert await service.is_watched(101, 1) is True

    @pytest.mark.asyncio
    async def test_get_watched_episodes(self, service):
        """Test getting all watched episodes for a show."""
        await service.mark_watched(101, 1)
        await service.mark_watched(102, 1)
        watched = await service.get_watched_episodes(1)
        assert len(watched) == 2


class TestCommentService:
    """Tests for CommentService."""

    @pytest.fixture
    def service(self):
        return CommentService(MockCommentRepository())

    @pytest.mark.asyncio
    async def test_add_show_comment(self, service):
        """Test adding a comment to a show."""
        comment = await service.add_comment(
            content="Great show!",
            show_id=1,
        )
        assert comment.id is not None
        assert comment.content == "Great show!"
        assert comment.episode_id is None

    @pytest.mark.asyncio
    async def test_add_episode_comment(self, service):
        """Test adding a comment to an episode."""
        comment = await service.add_comment(
            content="Amazing episode!",
            show_id=1,
            episode_id=101,
        )
        assert comment.episode_id == 101

    @pytest.mark.asyncio
    async def test_get_show_comments(self, service):
        """Test getting comments for a show."""
        await service.add_comment("Comment 1", show_id=1)
        await service.add_comment("Comment 2", show_id=1)
        await service.add_comment("Episode comment", show_id=1, episode_id=101)

        comments = await service.get_show_comments(1)
        assert len(comments) == 2  # Only show comments, not episode comments

    @pytest.mark.asyncio
    async def test_get_episode_comments(self, service):
        """Test getting comments for an episode."""
        await service.add_comment("Show comment", show_id=1)
        await service.add_comment("Episode comment", show_id=1, episode_id=101)

        comments = await service.get_episode_comments(1, 101)
        assert len(comments) == 1
        assert comments[0].content == "Episode comment"

    @pytest.mark.asyncio
    async def test_delete_comment(self, service):
        """Test deleting a comment."""
        comment = await service.add_comment("To delete", show_id=1)
        result = await service.delete_comment(comment.id)
        assert result is True

        comments = await service.get_show_comments(1)
        assert len(comments) == 0


class TestAIInsightService:
    """Tests for AIInsightService."""

    @pytest.fixture
    def mock_api(self):
        api = MockTVShowAPIClient()
        api.shows[1] = Show(id=1, name="Breaking Bad", genres=["Drama"])
        api.episodes[1] = [
            Episode(id=101, show_id=1, name="Pilot", season=1, number=1),
        ]
        return api

    @pytest.fixture
    def service(self, mock_api):
        return AIInsightService(
            ai_generator=MockAIInsightGenerator(),
            tv_api=mock_api,
            comment_repo=MockCommentRepository(),
        )

    @pytest.mark.asyncio
    async def test_get_show_insight(self, service):
        """Test generating insight for a show."""
        insight = await service.get_show_insight(1)
        assert insight is not None
        assert "Breaking Bad" in insight.content
        assert insight.show_id == 1
        assert insight.episode_id is None

    @pytest.mark.asyncio
    async def test_get_show_insight_not_found(self, service):
        """Test generating insight for non-existent show."""
        insight = await service.get_show_insight(999)
        assert insight is None

    @pytest.mark.asyncio
    async def test_get_episode_insight(self, service):
        """Test generating insight for an episode."""
        insight = await service.get_episode_insight(1, 101)
        assert insight is not None
        assert "Pilot" in insight.content
        assert insight.episode_id == 101

    @pytest.mark.asyncio
    async def test_get_episode_insight_not_found(self, service):
        """Test generating insight for non-existent episode."""
        insight = await service.get_episode_insight(1, 999)
        assert insight is None

