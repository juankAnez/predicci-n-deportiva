import json
from typing import Any, Optional

import redis

from src.config import settings


class RedisCache:
    def __init__(self):
        self.client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True,
        )
        self.default_ttl = 3600  # 1 hour

    def get(self, key: str) -> Optional[Any]:
        data = self.client.get(key)
        if data:
            try:
                return json.loads(data)
            except (json.JSONDecodeError, TypeError):
                return data
        return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        data = json.dumps(value, default=str)
        return self.client.setex(key, ttl or self.default_ttl, data)

    def delete(self, key: str) -> bool:
        return bool(self.client.delete(key))

    def exists(self, key: str) -> bool:
        return bool(self.client.exists(key))

    def clear_pattern(self, pattern: str) -> int:
        keys = self.client.keys(pattern)
        if keys:
            return self.client.delete(*keys)
        return 0

    def get_or_set(self, key: str, func, ttl: Optional[int] = None) -> Any:
        cached = self.get(key)
        if cached is not None:
            return cached
        value = func()
        self.set(key, value, ttl)
        return value


cache = RedisCache()
