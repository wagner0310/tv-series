from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, Text
from app.infrastructure.database import Base

class WatchedEpisodeModel(Base):
    """SQLAlchemy model for watched episodes."""

    __tablename__ = "watched_episodes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    episode_id = Column(Integer, nullable=False, index=True)
    show_id = Column(Integer, nullable=False, index=True)
    watched_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<WatchedEpisode(id={self.id}, episode_id={self.episode_id}, show_id={self.show_id})>"


class CommentModel(Base):
    """SQLAlchemy model for comments."""

    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(Text, nullable=False)
    show_id = Column(Integer, nullable=False, index=True)
    episode_id = Column(Integer, nullable=True, index=True)  # None = show comment
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<Comment(id={self.id}, show_id={self.show_id}, episode_id={self.episode_id})>"

