from fastapi import APIRouter, HTTPException, status

from app.api.dependencies import (
    AIInsightServiceDep,
    CommentServiceDep,
    EpisodeTrackingServiceDep,
    ShowServiceDep,
)
from app.api.schemas import (
    AIInsightRequest,
    AIInsightSchema,
    CommentSchema,
    CommentsResponse,
    CreateCommentRequest,
    EpisodeSchema,
    MarkWatchedRequest,
    SearchResponseSchema,
    SearchResultSchema,
    SeasonEpisodesSchema,
    ShowDetailSchema,
    ShowSchema,
    WatchedEpisodeSchema,
    WatchedEpisodesResponse,
)

router = APIRouter()


# Search routes
@router.get("/search", response_model=SearchResponseSchema)
async def search_shows(
    q: str,
    show_service: ShowServiceDep,
) -> SearchResponseSchema:
    """Search for TV shows by query."""
    results = await show_service.search_shows(q)
    return SearchResponseSchema(
        results=[
            SearchResultSchema(
                score=r.score,
                show=ShowSchema(
                    id=r.show.id,
                    name=r.show.name,
                    summary=r.show.summary,
                    image_url=r.show.image_url,
                    premiered=r.show.premiered,
                    genres=r.show.genres,
                    rating=r.show.rating,
                    status=r.show.status,
                    official_site=r.show.official_site,
                ),
            )
            for r in results
        ],
        query=q,
    )


# Show detail routes
@router.get("/shows/{show_id}", response_model=ShowDetailSchema)
async def get_show_details(
    show_id: int,
    show_service: ShowServiceDep,
) -> ShowDetailSchema:
    """Get detailed information about a show including episodes by season."""
    show = await show_service.get_show_details(show_id)
    if not show:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Show with ID {show_id} not found",
        )

    seasons_dict = await show_service.get_episodes_by_season(show_id)
    seasons = [
        SeasonEpisodesSchema(
            season=season_num,
            episodes=[
                EpisodeSchema(
                    id=ep.id,
                    show_id=ep.show_id,
                    name=ep.name,
                    season=ep.season,
                    number=ep.number,
                    summary=ep.summary,
                    airdate=ep.airdate,
                    runtime=ep.runtime,
                    image_url=ep.image_url,
                )
                for ep in episodes
            ],
        )
        for season_num, episodes in seasons_dict.items()
    ]

    return ShowDetailSchema(
        show=ShowSchema(
            id=show.id,
            name=show.name,
            summary=show.summary,
            image_url=show.image_url,
            premiered=show.premiered,
            genres=show.genres,
            rating=show.rating,
            status=show.status,
            official_site=show.official_site,
        ),
        seasons=seasons,
    )


# Watched episode routes
@router.get("/shows/{show_id}/watched", response_model=WatchedEpisodesResponse)
async def get_watched_episodes(
    show_id: int,
    tracking_service: EpisodeTrackingServiceDep,
) -> WatchedEpisodesResponse:
    """Get all watched episodes for a show."""
    watched = await tracking_service.get_watched_episodes(show_id)
    return WatchedEpisodesResponse(
        show_id=show_id,
        episode_ids=[w.episode_id for w in watched],
    )


@router.post("/watched", response_model=WatchedEpisodeSchema, status_code=status.HTTP_201_CREATED)
async def mark_episode_watched(
    request: MarkWatchedRequest,
    tracking_service: EpisodeTrackingServiceDep,
) -> WatchedEpisodeSchema:
    """Mark an episode as watched."""
    watched = await tracking_service.mark_watched(request.episode_id, request.show_id)
    return WatchedEpisodeSchema(
        id=watched.id,
        episode_id=watched.episode_id,
        show_id=watched.show_id,
        watched_at=watched.watched_at,
    )


@router.delete("/watched/{show_id}/{episode_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unmark_episode_watched(
    show_id: int,
    episode_id: int,
    tracking_service: EpisodeTrackingServiceDep,
) -> None:
    """Unmark an episode as watched."""
    deleted = await tracking_service.unmark_watched(episode_id, show_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Watched episode not found",
        )


# Comment routes
@router.get("/shows/{show_id}/comments", response_model=CommentsResponse)
async def get_show_comments(
    show_id: int,
    comment_service: CommentServiceDep,
) -> CommentsResponse:
    """Get all comments for a show (excluding episode-specific comments)."""
    comments = await comment_service.get_show_comments(show_id)
    return CommentsResponse(
        comments=[
            CommentSchema(
                id=c.id,
                content=c.content,
                show_id=c.show_id,
                episode_id=c.episode_id,
                created_at=c.created_at,
            )
            for c in comments
        ]
    )


@router.get("/shows/{show_id}/episodes/{episode_id}/comments", response_model=CommentsResponse)
async def get_episode_comments(
    show_id: int,
    episode_id: int,
    comment_service: CommentServiceDep,
) -> CommentsResponse:
    """Get comments for a specific episode."""
    comments = await comment_service.get_episode_comments(show_id, episode_id)
    return CommentsResponse(
        comments=[
            CommentSchema(
                id=c.id,
                content=c.content,
                show_id=c.show_id,
                episode_id=c.episode_id,
                created_at=c.created_at,
            )
            for c in comments
        ]
    )


@router.post("/comments", response_model=CommentSchema, status_code=status.HTTP_201_CREATED)
async def create_comment(
    request: CreateCommentRequest,
    comment_service: CommentServiceDep,
) -> CommentSchema:
    """Create a new comment on a show or episode."""
    comment = await comment_service.add_comment(
        content=request.content,
        show_id=request.show_id,
        episode_id=request.episode_id,
    )
    return CommentSchema(
        id=comment.id,  # type: ignore
        content=comment.content,
        show_id=comment.show_id,
        episode_id=comment.episode_id,
        created_at=comment.created_at,
    )


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: int,
    comment_service: CommentServiceDep,
) -> None:
    """Delete a comment."""
    deleted = await comment_service.delete_comment(comment_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )


# AI Insight routes
@router.post("/insights", response_model=AIInsightSchema)
async def generate_insight(
    request: AIInsightRequest,
    ai_service: AIInsightServiceDep,
) -> AIInsightSchema:
    """Generate an AI insight for a show or episode."""
    if request.episode_id:
        insight = await ai_service.get_episode_insight(
            show_id=request.show_id,
            episode_id=request.episode_id,
            include_comments=request.include_comments,
        )
    else:
        insight = await ai_service.get_show_insight(
            show_id=request.show_id,
            include_comments=request.include_comments,
        )

    if not insight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Show or episode not found",
        )

    return AIInsightSchema(
        content=insight.content,
        show_id=insight.show_id,
        episode_id=insight.episode_id,
        generated_at=insight.generated_at,
    )


# Health check
@router.get("/health")
async def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "healthy"}

