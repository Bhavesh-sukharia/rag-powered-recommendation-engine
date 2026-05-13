"""
Redis connection manager.
"""
import redis
from typing import Optional
from .config import get_settings


class RedisClient:
    """Singleton Redis client."""
    
    _instance: Optional[redis.Redis] = None
    
    @classmethod
    def get_client(cls) -> redis.Redis:
        """Get or create Redis client."""
        if cls._instance is None:
            settings = get_settings()
            cls._instance = redis.from_url(settings.REDIS_URL, decode_responses=True)
        return cls._instance
    
    @classmethod
    def close(cls):
        """Close Redis connection."""
        if cls._instance:
            cls._instance.close()
            cls._instance = None
