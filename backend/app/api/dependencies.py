from typing import Annotated, AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services import (
    AIInsightService,
    CommentService,
    EpisodeTrackingService,
    ShowService,
)
from app.infrastructure.ai_generator import HuggingFaceInsightGenerator
from app.infrastructure.database import get_session
from app.infrastructure.repositories import SQLAlchemyCommentRepository, SQLAlchemyShowRepository
from app.infrastructure.tvmaze_client import TVMazeClient


# Database session dependency
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session."""
    async for session in get_session():
        yield session


DBSession = Annotated[AsyncSession, Depends(get_db_session)]


# Infrastructure dependencies
def get_tvmaze_client() -> TVMazeClient:
    """Get TVMaze API client."""
    return TVMazeClient()


def get_ai_generator() -> HuggingFaceInsightGenerator:
    """Get AI insight generator."""
    return HuggingFaceInsightGenerator()


# Repository dependencies
def get_show_repository(session: DBSession) -> SQLAlchemyShowRepository:
    """Get show repository."""
    return SQLAlchemyShowRepository(session)


def get_comment_repository(session: DBSession) -> SQLAlchemyCommentRepository:
    """Get comment repository."""
    return SQLAlchemyCommentRepository(session)


# Service dependencies
def get_show_service(
    session: DBSession,
    tv_client: Annotated[TVMazeClient, Depends(get_tvmaze_client)],
) -> ShowService:
    """Get show service."""
    show_repo = SQLAlchemyShowRepository(session)
    comment_repo = SQLAlchemyCommentRepository(session)
    return ShowService(tv_client, show_repo, comment_repo)


def get_episode_tracking_service(session: DBSession) -> EpisodeTrackingService:
    """Get episode tracking service."""
    show_repo = SQLAlchemyShowRepository(session)
    return EpisodeTrackingService(show_repo)


def get_comment_service(session: DBSession) -> CommentService:
    """Get comment service."""
    comment_repo = SQLAlchemyCommentRepository(session)
    return CommentService(comment_repo)


def get_ai_insight_service(
    session: DBSession,
    tv_client: Annotated[TVMazeClient, Depends(get_tvmaze_client)],
    ai_generator: Annotated[HuggingFaceInsightGenerator, Depends(get_ai_generator)],
) -> AIInsightService:
    """Get AI insight service."""
    comment_repo = SQLAlchemyCommentRepository(session)
    return AIInsightService(ai_generator, tv_client, comment_repo)


# Type aliases for cleaner route signatures
ShowServiceDep = Annotated[ShowService, Depends(get_show_service)]
EpisodeTrackingServiceDep = Annotated[EpisodeTrackingService, Depends(get_episode_tracking_service)]
CommentServiceDep = Annotated[CommentService, Depends(get_comment_service)]
AIInsightServiceDep = Annotated[AIInsightService, Depends(get_ai_insight_service)]

