import logging
import os
import re
from typing import Optional

import httpx

from app.domain.entities import AIInsight, Comment, Episode, Show
from app.domain.interfaces import AIInsightGenerator

logger = logging.getLogger(__name__)

HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models"
DEFAULT_MODEL = "mistralai/Mistral-7B-Instruct-v0.2"


def strip_html_tags(text: str) -> str:
    """Remove HTML tags from text."""
    if not text:
        return ""
    clean = re.sub(r"<[^>]+>", "", text)
    return clean.strip()


class HuggingFaceInsightGenerator(AIInsightGenerator):
    """Implementation of AIInsightGenerator using HuggingFace Inference API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = DEFAULT_MODEL,
        timeout: float = 30.0,
    ):
        self._api_key = api_key or os.getenv("HUGGINGFACE_API_KEY", "")
        self._model = model
        self._timeout = timeout
        self._fallback_enabled = True

    def _build_show_prompt(
        self,
        show: Show,
        comments: Optional[list[Comment]] = None,
    ) -> str:
        """Build prompt for show insight generation."""
        summary = strip_html_tags(show.summary) if show.summary else "No summary available"
        genres = ", ".join(show.genres) if show.genres else "Unknown"

        prompt = f"""<s>[INST] Generate a brief, insightful analysis (2-3 sentences) for this TV series.

Series: {show.name}
Genres: {genres}
Summary: {summary}
"""
        if comments:
            comment_texts = [c.content for c in comments[:5]]  # Limit to 5 comments
            prompt += f"\nUser Comments: {'; '.join(comment_texts)}\n"

        prompt += """
Focus on themes, appeal to specific audiences, and what makes it interesting.
Respond with ONLY the insight, no additional text. [/INST]"""

        return prompt

    def _build_episode_prompt(
        self,
        episode: Episode,
        show: Show,
        comments: Optional[list[Comment]] = None,
    ) -> str:
        """Build prompt for episode insight generation."""
        episode_summary = strip_html_tags(episode.summary) if episode.summary else "No summary available"
        show_summary = strip_html_tags(show.summary) if show.summary else "No summary available"
        genres = ", ".join(show.genres) if show.genres else "Unknown"

        prompt = f"""<s>[INST] Generate a brief, insightful analysis (2-3 sentences) for this TV episode.

Series: {show.name}
Series Genres: {genres}
Series Summary: {show_summary}

Episode: S{episode.season:02d}E{episode.number:02d} - {episode.name}
Episode Summary: {episode_summary}
"""
        if comments:
            comment_texts = [c.content for c in comments[:5]]
            prompt += f"\nUser Comments: {'; '.join(comment_texts)}\n"

        prompt += """
Focus on themes, character development, and how it fits within the series.
Respond with ONLY the insight, no additional text. [/INST]"""

        return prompt

    def _generate_fallback_show_insight(self, show: Show) -> str:
        """Generate a fallback insight when AI is unavailable."""
        genres = show.genres[:3] if show.genres else ["drama"]
        genre_text = " and ".join(genres) if len(genres) <= 2 else f"{', '.join(genres[:-1])}, and {genres[-1]}"

        templates = [
            f"'{show.name}' is a compelling {genre_text} series that offers viewers an engaging narrative experience.",
            f"This {genre_text} series explores complex themes through its storytelling and character dynamics.",
            f"Fans of {genre_text} will find '{show.name}' to be a captivating watch with its unique perspective.",
        ]

        # Simple deterministic selection based on show ID
        return templates[show.id % len(templates)]

    def _generate_fallback_episode_insight(self, episode: Episode, show: Show) -> str:
        """Generate a fallback insight when AI is unavailable."""
        return (
            f"Episode {episode.number} of Season {episode.season} continues the narrative "
            f"of '{show.name}', advancing the story while developing its characters. "
            f"This episode contributes to the overall arc of the series."
        )

    async def _call_huggingface_api(self, prompt: str) -> Optional[str]:
        """Make API call to HuggingFace Inference API."""
        if not self._api_key:
            logger.warning("No HuggingFace API key configured")
            return None

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 150,
                "temperature": 0.7,
                "do_sample": True,
                "return_full_text": False,
            },
        }

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(
                    f"{HUGGINGFACE_API_URL}/{self._model}",
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()
                result = response.json()

                if isinstance(result, list) and len(result) > 0:
                    generated_text = result[0].get("generated_text", "")
                    return generated_text.strip()

                return None

        except httpx.HTTPStatusError as e:
            logger.error(f"HuggingFace API error: {e.response.status_code} - {e.response.text}")
            return None
        except httpx.HTTPError as e:
            logger.error(f"HuggingFace API connection error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error calling HuggingFace API: {e}")
            return None

    async def generate_show_insight(
        self,
        show: Show,
        comments: Optional[list[Comment]] = None,
    ) -> AIInsight:
        """Generate an AI insight for a TV show."""
        prompt = self._build_show_prompt(show, comments)
        insight_text = await self._call_huggingface_api(prompt)

        if not insight_text and self._fallback_enabled:
            logger.info(f"Using fallback insight for show {show.id}")
            insight_text = self._generate_fallback_show_insight(show)

        return AIInsight(
            content=insight_text or "Unable to generate insight at this time.",
            show_id=show.id,
            episode_id=None,
        )

    async def generate_episode_insight(
        self,
        episode: Episode,
        show: Show,
        comments: Optional[list[Comment]] = None,
    ) -> AIInsight:
        """Generate an AI insight for an episode."""
        prompt = self._build_episode_prompt(episode, show, comments)
        insight_text = await self._call_huggingface_api(prompt)

        if not insight_text and self._fallback_enabled:
            logger.info(f"Using fallback insight for episode {episode.id}")
            insight_text = self._generate_fallback_episode_insight(episode, show)

        return AIInsight(
            content=insight_text or "Unable to generate insight at this time.",
            show_id=show.id,
            episode_id=episode.id,
        )

