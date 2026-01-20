from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import Comment, WatchedEpisode
from app.domain.interfaces import CommentRepository, ShowRepository
from app.infrastructure.models import CommentModel, WatchedEpisodeModel


class SQLAlchemyShowRepository(ShowRepository):
    """SQLAlchemy implementation of ShowRepository."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_watched_episodes(self, show_id: int) -> list[WatchedEpisode]:
        """Get all watched episodes for a show."""
        result = await self._session.execute(
            select(WatchedEpisodeModel).where(WatchedEpisodeModel.show_id == show_id)
        )
        rows = result.scalars().all()
        return [
            WatchedEpisode(
                id=row.id,
                episode_id=row.episode_id,
                show_id=row.show_id,
                watched_at=row.watched_at,
            )
            for row in rows
        ]

    async def mark_episode_watched(self, episode_id: int, show_id: int) -> WatchedEpisode:
        """Mark an episode as watched."""
        # Check if already watched
        result = await self._session.execute(
            select(WatchedEpisodeModel).where(
                WatchedEpisodeModel.episode_id == episode_id,
                WatchedEpisodeModel.show_id == show_id,
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            return WatchedEpisode(
                id=existing.id,
                episode_id=existing.episode_id,
                show_id=existing.show_id,
                watched_at=existing.watched_at,
            )

        model = WatchedEpisodeModel(episode_id=episode_id, show_id=show_id)
        self._session.add(model)
        await self._session.flush()
        return WatchedEpisode(
            id=model.id,
            episode_id=model.episode_id,
            show_id=model.show_id,
            watched_at=model.watched_at,
        )

    async def unmark_episode_watched(self, episode_id: int, show_id: int) -> bool:
        """Unmark an episode as watched."""
        result = await self._session.execute(
            delete(WatchedEpisodeModel).where(
                WatchedEpisodeModel.episode_id == episode_id,
                WatchedEpisodeModel.show_id == show_id,
            )
        )
        return result.rowcount > 0

    async def is_episode_watched(self, episode_id: int, show_id: int) -> bool:
        """Check if an episode is marked as watched."""
        result = await self._session.execute(
            select(WatchedEpisodeModel).where(
                WatchedEpisodeModel.episode_id == episode_id,
                WatchedEpisodeModel.show_id == show_id,
            )
        )
        return result.scalar_one_or_none() is not None


class SQLAlchemyCommentRepository(CommentRepository):
    """SQLAlchemy implementation of CommentRepository."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_comments_for_show(self, show_id: int) -> list[Comment]:
        """Get all comments for a show (including episode comments)."""
        result = await self._session.execute(
            select(CommentModel)
            .where(CommentModel.show_id == show_id)
            .order_by(CommentModel.created_at.desc())
        )
        rows = result.scalars().all()
        return [
            Comment(
                id=row.id,
                content=row.content,
                show_id=row.show_id,
                episode_id=row.episode_id,
                created_at=row.created_at,
            )
            for row in rows
        ]

    async def get_comments_for_episode(self, show_id: int, episode_id: int) -> list[Comment]:
        """Get comments for a specific episode."""
        result = await self._session.execute(
            select(CommentModel)
            .where(
                CommentModel.show_id == show_id,
                CommentModel.episode_id == episode_id,
            )
            .order_by(CommentModel.created_at.desc())
        )
        rows = result.scalars().all()
        return [
            Comment(
                id=row.id,
                content=row.content,
                show_id=row.show_id,
                episode_id=row.episode_id,
                created_at=row.created_at,
            )
            for row in rows
        ]

    async def add_comment(self, comment: Comment) -> Comment:
        """Add a new comment."""
        model = CommentModel(
            content=comment.content,
            show_id=comment.show_id,
            episode_id=comment.episode_id,
        )
        self._session.add(model)
        await self._session.flush()
        return Comment(
            id=model.id,
            content=model.content,
            show_id=model.show_id,
            episode_id=model.episode_id,
            created_at=model.created_at,
        )

    async def delete_comment(self, comment_id: int) -> bool:
        """Delete a comment."""
        result = await self._session.execute(
            delete(CommentModel).where(CommentModel.id == comment_id)
        )
        return result.rowcount > 0

