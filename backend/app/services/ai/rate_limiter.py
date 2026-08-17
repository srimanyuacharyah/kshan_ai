import time
from typing import Dict, List
from backend.app.services.ai.exceptions import RateLimitExceededError
from backend.app.core.logging import logger

class UserGenerationRateLimiter:
    """
    In-memory rate limiter per user_id to prevent abuse and API quota exhaustion.
    Configured for 30 AI generations per minute per user by default.
    """

    def __init__(self, max_requests: int = 30, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._user_timestamps: Dict[str, List[float]] = {}

    def check_and_record(self, user_id: str):
        now = time.time()
        timestamps = self._user_timestamps.setdefault(user_id, [])

        # Filter timestamps outside sliding window
        valid_timestamps = [t for t in timestamps if now - t < self.window_seconds]
        self._user_timestamps[user_id] = valid_timestamps

        if len(valid_timestamps) >= self.max_requests:
            logger.warning(f"Rate limit exceeded for user_id={user_id} ({len(valid_timestamps)}/{self.max_requests} in {self.window_seconds}s)")
            raise RateLimitExceededError(
                f"Rate limit exceeded: You can make at most {self.max_requests} generations per {self.window_seconds} seconds."
            )

        valid_timestamps.append(now)

rate_limiter = UserGenerationRateLimiter()
