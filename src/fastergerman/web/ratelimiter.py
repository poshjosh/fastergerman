from datetime import datetime


class RateLimiter:
    def __init__(self, default_permits: int, default_duration: float, cache: dict[str, (int, float)] = None):
        self.__default_permits = default_permits
        self.__default_duration = default_duration
        self.__cache = cache if cache else {}

    def is_within_limit(self, key: str, permits: int = -1, duration: float = -1) -> bool:
        if permits < 0:
            permits = self.__default_permits
        if duration < 0:
            duration = self.__default_duration
        if permits < 0 or duration < 0:
            return True
        curr_timestamp = datetime.now().timestamp()
        val = self.__cache.get(key)
        hits, last_access_timestamp = val if val else (None, None)
        if last_access_timestamp is None or (curr_timestamp - last_access_timestamp) > duration:
            self.__cache[key] = 1, curr_timestamp
            return True
        if hits + 1 <= permits:
            self.__cache[key] = hits + 1, curr_timestamp
            return True
        return False