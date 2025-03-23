import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class RateLimiter:
    def __init__(self, permits: int, duration: float, cache: dict[str, (int, float)] = None):
        if permits < 0:
            raise ValueError("Permits must be greater or equal to 0")
        if duration < 0:
            raise ValueError("Duration must be greater or equal to 0")
        self.__permits = permits
        self.__duration = duration
        self.__cache = cache if cache else {}

    def is_within_limit(self, key: str) -> bool:
        curr_timestamp = datetime.now().timestamp()
        permits, start_timestamp = self.__cache.get(key, (0, curr_timestamp))
        duration = int((curr_timestamp - start_timestamp) * 1000)
        within_limit = duration > self.__duration or permits + 1 <= self.__permits
        if duration > self.__duration:
            self.__cache[key] = 1, curr_timestamp
        else:
            self.__cache[key] = permits + 1, start_timestamp
        logger.debug(f"For: {key}, limit exceeded: {within_limit is False}, "
                     f"({permits + 1} in {duration} millis) "
                     f"> ({self.__permits} in {self.__duration} millis)")
        return within_limit