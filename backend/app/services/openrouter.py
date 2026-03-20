import asyncio
import json
import logging
import time
from collections import deque

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class RateLimiter:
    """Sliding-window rate limiter."""

    def __init__(self, max_requests: int, period_seconds: float = 60.0):
        self._max = max_requests
        self._period = period_seconds
        self._timestamps: deque[float] = deque()
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        async with self._lock:
            now = time.monotonic()
            while self._timestamps and self._timestamps[0] < now - self._period:
                self._timestamps.popleft()
            if len(self._timestamps) >= self._max:
                sleep_time = self._period - (now - self._timestamps[0])
                logger.debug("Rate limit: sleeping %.1fs", sleep_time)
                await asyncio.sleep(sleep_time)
            self._timestamps.append(time.monotonic())


class OpenRouterClient:
    def __init__(self) -> None:
        self._client: httpx.AsyncClient | None = None
        self._rate_limiter = RateLimiter(settings.OPENROUTER_RATE_LIMIT)

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=settings.OPENROUTER_BASE_URL,
                headers={
                    "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                },
                timeout=120.0,
            )
        return self._client

    async def chat(
        self,
        system: str,
        user: str,
        model: str | None = None,
        temperature: float = 0.1,
        max_tokens: int = 2048,
    ) -> str:
        """Send a chat completion request. Returns the assistant message content."""
        await self._rate_limiter.acquire()
        client = await self._get_client()
        payload = {
            "model": model or settings.OPENROUTER_MODEL,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        for attempt in range(3):
            response = await client.post("/chat/completions", json=payload)
            if response.status_code == 429:
                wait = 2**attempt * 5
                logger.warning("Rate limited (429), retrying in %ds", wait)
                await asyncio.sleep(wait)
                continue
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]

        raise RuntimeError("OpenRouter rate limit exceeded after 3 retries")

    async def chat_json(
        self,
        system: str,
        user: str,
        model: str | None = None,
    ) -> list | dict:
        """Send chat request and parse JSON response. Falls back to empty list on parse error."""
        raw = await self.chat(system, user, model=model)
        # Strip markdown code fences if present
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            lines = lines[1:]  # remove opening fence
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            cleaned = "\n".join(lines)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            logger.warning("Failed to parse LLM JSON response: %s", raw[:200])
            return []

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()
