import logging
from typing import Optional
import httpx

from app.domain.entities import Episode, SearchResult, Show
from app.domain.interfaces import TVShowAPIClient

logger = logging.getLogger(__name__)

TVMAZE_BASE_URL = "https://api.tvmaze.com"


class TVMazeClient(TVShowAPIClient):
    """Implementation of TVShowAPIClient using TVMaze API."""

    def __init__(self, timeout: float = 10.0):
        self._timeout = timeout

    def _parse_show(self, data: dict) -> Show:
        """Parse show data from TVMaze API response."""
        image = data.get("image")
        image_url = image.get("medium") or image.get("original") if image else None
        rating = data.get("rating", {})

        return Show(
            id=data["id"],
            name=data["name"],
            summary=data.get("summary"),
            image_url=image_url,
            premiered=data.get("premiered"),
            genres=data.get("genres", []),
            rating=rating.get("average") if rating else None,
            status=data.get("status"),
            official_site=data.get("officialSite"),
        )

    def _parse_episode(self, data: dict, show_id: int) -> Episode:
        """Parse episode data from TVMaze API response."""
        image = data.get("image")
        image_url = image.get("medium") or image.get("original") if image else None

        return Episode(
            id=data["id"],
            show_id=show_id,
            name=data["name"],
            season=data["season"],
            number=data.get("number", 0),
            summary=data.get("summary"),
            airdate=data.get("airdate"),
            runtime=data.get("runtime"),
            image_url=image_url,
        )

    async def search_shows(self, query: str) -> list[SearchResult]:
        """Search for TV shows by query."""
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.get(
                    f"{TVMAZE_BASE_URL}/search/shows",
                    params={"q": query},
                )
                response.raise_for_status()
                data = response.json()

                return [
                    SearchResult(
                        score=item.get("score", 0),
                        show=self._parse_show(item["show"]),
                    )
                    for item in data
                ]
        except httpx.HTTPError as e:
            logger.error(f"Error searching shows: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error searching shows: {e}")
            return []

    async def get_show(self, show_id: int) -> Optional[Show]:
        """Get show details by ID."""
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.get(f"{TVMAZE_BASE_URL}/shows/{show_id}")
                response.raise_for_status()
                data = response.json()
                return self._parse_show(data)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            logger.error(f"Error fetching show {show_id}: {e}")
            return None
        except httpx.HTTPError as e:
            logger.error(f"Error fetching show {show_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching show {show_id}: {e}")
            return None

    async def get_episodes(self, show_id: int) -> list[Episode]:
        """Get all episodes for a show."""
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.get(f"{TVMAZE_BASE_URL}/shows/{show_id}/episodes")
                response.raise_for_status()
                data = response.json()
                return [self._parse_episode(ep, show_id) for ep in data]
        except httpx.HTTPError as e:
            logger.error(f"Error fetching episodes for show {show_id}: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching episodes for show {show_id}: {e}")
            return []

