"""Tests for domain entities."""
from datetime import datetime

from app.domain.entities import (
    AIInsight,
    Comment,
    Episode,
    SearchResult,
    Show,
    WatchedEpisode,
)


class TestShow:
    """Tests for Show entity."""

    def test_create_show_with_required_fields(self):
        """Test creating a show with required fields only."""
        show = Show(id=1, name="Test Show")
        assert show.id == 1
        assert show.name == "Test Show"
        assert show.summary is None
        assert show.genres == []

    def test_create_show_with_all_fields(self):
        """Test creating a show with all fields."""
        show = Show(
            id=1,
            name="Breaking Bad",
            summary="A chemistry teacher becomes a drug lord.",
            image_url="https://example.com/image.jpg",
            premiered="2008-01-20",
            genres=["Drama", "Crime", "Thriller"],
            rating=9.5,
            status="Ended",
            official_site="https://www.amc.com/shows/breaking-bad",
        )
        assert show.id == 1
        assert show.name == "Breaking Bad"
        assert len(show.genres) == 3
        assert show.rating == 9.5


class TestEpisode:
    """Tests for Episode entity."""

    def test_create_episode(self):
        """Test creating an episode."""
        episode = Episode(
            id=100,
            show_id=1,
            name="Pilot",
            season=1,
            number=1,
            summary="Walter White starts cooking meth.",
            airdate="2008-01-20",
            runtime=58,
        )
        assert episode.id == 100
        assert episode.show_id == 1
        assert episode.season == 1
        assert episode.number == 1


class TestWatchedEpisode:
    """Tests for WatchedEpisode entity."""

    def test_create_watched_episode(self):
        """Test creating a watched episode record."""
        watched = WatchedEpisode(
            id=1,
            episode_id=100,
            show_id=1,
        )
        assert watched.id == 1
        assert watched.episode_id == 100
        assert isinstance(watched.watched_at, datetime)


class TestComment:
    """Tests for Comment entity."""

    def test_create_show_comment(self):
        """Test creating a comment on a show."""
        comment = Comment(
            id=1,
            content="Great show!",
            show_id=1,
            episode_id=None,
        )
        assert comment.id == 1
        assert comment.content == "Great show!"
        assert comment.episode_id is None

    def test_create_episode_comment(self):
        """Test creating a comment on an episode."""
        comment = Comment(
            id=2,
            content="Amazing episode!",
            show_id=1,
            episode_id=100,
        )
        assert comment.episode_id == 100


class TestSearchResult:
    """Tests for SearchResult entity."""

    def test_create_search_result(self):
        """Test creating a search result."""
        show = Show(id=1, name="Test Show")
        result = SearchResult(score=0.95, show=show)
        assert result.score == 0.95
        assert result.show.name == "Test Show"


class TestAIInsight:
    """Tests for AIInsight entity."""

    def test_create_show_insight(self):
        """Test creating an insight for a show."""
        insight = AIInsight(
            content="This show explores themes of morality.",
            show_id=1,
            episode_id=None,
        )
        assert insight.show_id == 1
        assert insight.episode_id is None

    def test_create_episode_insight(self):
        """Test creating an insight for an episode."""
        insight = AIInsight(
            content="This episode focuses on character development.",
            show_id=1,
            episode_id=100,
        )
        assert insight.episode_id == 100

