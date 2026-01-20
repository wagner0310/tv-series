"""Tests for repository implementations."""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import Comment
from app.infrastructure.repositories import (
    SQLAlchemyCommentRepository,
    SQLAlchemyShowRepository,
)


class TestSQLAlchemyShowRepository:
    """Tests for SQLAlchemyShowRepository."""

    @pytest.mark.asyncio
    async def test_mark_episode_watched(self, db_session: AsyncSession):
        """Test marking an episode as watched."""
        repo = SQLAlchemyShowRepository(db_session)

        watched = await repo.mark_episode_watched(episode_id=101, show_id=1)

        assert watched.id is not None
        assert watched.episode_id == 101
        assert watched.show_id == 1

    @pytest.mark.asyncio
    async def test_mark_episode_watched_idempotent(self, db_session: AsyncSession):
        """Test marking same episode watched multiple times returns same record."""
        repo = SQLAlchemyShowRepository(db_session)

        watched1 = await repo.mark_episode_watched(episode_id=101, show_id=1)
        watched2 = await repo.mark_episode_watched(episode_id=101, show_id=1)

        assert watched1.id == watched2.id

    @pytest.mark.asyncio
    async def test_unmark_episode_watched(self, db_session: AsyncSession):
        """Test unmarking an episode as watched."""
        repo = SQLAlchemyShowRepository(db_session)

        await repo.mark_episode_watched(episode_id=101, show_id=1)
        result = await repo.unmark_episode_watched(episode_id=101, show_id=1)

        assert result is True
        assert await repo.is_episode_watched(101, 1) is False

    @pytest.mark.asyncio
    async def test_unmark_episode_not_watched(self, db_session: AsyncSession):
        """Test unmarking an episode that wasn't watched."""
        repo = SQLAlchemyShowRepository(db_session)

        result = await repo.unmark_episode_watched(episode_id=999, show_id=1)

        assert result is False

    @pytest.mark.asyncio
    async def test_get_watched_episodes(self, db_session: AsyncSession):
        """Test getting all watched episodes for a show."""
        repo = SQLAlchemyShowRepository(db_session)

        await repo.mark_episode_watched(101, 1)
        await repo.mark_episode_watched(102, 1)
        await repo.mark_episode_watched(201, 2)  # Different show

        watched = await repo.get_watched_episodes(1)

        assert len(watched) == 2
        episode_ids = {w.episode_id for w in watched}
        assert episode_ids == {101, 102}

    @pytest.mark.asyncio
    async def test_is_episode_watched(self, db_session: AsyncSession):
        """Test checking if an episode is watched."""
        repo = SQLAlchemyShowRepository(db_session)

        assert await repo.is_episode_watched(101, 1) is False

        await repo.mark_episode_watched(101, 1)

        assert await repo.is_episode_watched(101, 1) is True


class TestSQLAlchemyCommentRepository:
    """Tests for SQLAlchemyCommentRepository."""

    @pytest.mark.asyncio
    async def test_add_comment(self, db_session: AsyncSession):
        """Test adding a comment."""
        repo = SQLAlchemyCommentRepository(db_session)
        comment = Comment(id=None, content="Great show!", show_id=1)

        result = await repo.add_comment(comment)

        assert result.id is not None
        assert result.content == "Great show!"
        assert result.show_id == 1

    @pytest.mark.asyncio
    async def test_add_episode_comment(self, db_session: AsyncSession):
        """Test adding a comment to an episode."""
        repo = SQLAlchemyCommentRepository(db_session)
        comment = Comment(id=None, content="Amazing episode!", show_id=1, episode_id=101)

        result = await repo.add_comment(comment)

        assert result.episode_id == 101

    @pytest.mark.asyncio
    async def test_get_comments_for_show(self, db_session: AsyncSession):
        """Test getting all comments for a show."""
        repo = SQLAlchemyCommentRepository(db_session)

        await repo.add_comment(Comment(id=None, content="Comment 1", show_id=1))
        await repo.add_comment(Comment(id=None, content="Comment 2", show_id=1))
        await repo.add_comment(Comment(id=None, content="Other show", show_id=2))

        comments = await repo.get_comments_for_show(1)

        assert len(comments) == 2

    @pytest.mark.asyncio
    async def test_get_comments_for_episode(self, db_session: AsyncSession):
        """Test getting comments for a specific episode."""
        repo = SQLAlchemyCommentRepository(db_session)

        await repo.add_comment(Comment(id=None, content="Show comment", show_id=1))
        await repo.add_comment(
            Comment(id=None, content="Episode 101 comment", show_id=1, episode_id=101)
        )
        await repo.add_comment(
            Comment(id=None, content="Episode 102 comment", show_id=1, episode_id=102)
        )

        comments = await repo.get_comments_for_episode(1, 101)

        assert len(comments) == 1
        assert comments[0].content == "Episode 101 comment"

    @pytest.mark.asyncio
    async def test_delete_comment(self, db_session: AsyncSession):
        """Test deleting a comment."""
        repo = SQLAlchemyCommentRepository(db_session)
        comment = await repo.add_comment(Comment(id=None, content="To delete", show_id=1))

        result = await repo.delete_comment(comment.id)  # type: ignore

        assert result is True

    @pytest.mark.asyncio
    async def test_delete_nonexistent_comment(self, db_session: AsyncSession):
        """Test deleting a comment that doesn't exist."""
        repo = SQLAlchemyCommentRepository(db_session)

        result = await repo.delete_comment(9999)

        assert result is False

    @pytest.mark.asyncio
    async def test_comments_ordered_by_date(self, db_session: AsyncSession):
        """Test that comments are returned in reverse chronological order."""
        repo = SQLAlchemyCommentRepository(db_session)

        await repo.add_comment(Comment(id=None, content="First", show_id=1))
        await repo.add_comment(Comment(id=None, content="Second", show_id=1))
        await repo.add_comment(Comment(id=None, content="Third", show_id=1))

        comments = await repo.get_comments_for_show(1)

        # Most recent first
        assert comments[0].content == "Third"
        assert comments[2].content == "First"

