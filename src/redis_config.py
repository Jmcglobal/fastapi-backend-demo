import redis
import os
from dotenv import load_dotenv
from typing import Optional
import json

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

redis_client = redis.from_url(REDIS_URL, decode_responses=True)


def get_redis_client():
    """Get Redis client instance"""
    return redis_client


def set_cache(key: str, value: dict, ttl: int = 600) -> bool:
    """
    Set a value in Redis cache with TTL (Time To Live)
    Default TTL is 600 seconds (10 minutes)
    """
    try:
        redis_client.setex(key, ttl, json.dumps(value))
        return True
    except Exception as e:
        print(f"Error setting cache: {e}")
        return False


def get_cache(key: str) -> Optional[dict]:
    """Get a value from Redis cache"""
    try:
        value = redis_client.get(key)
        if value:
            return json.loads(value)
        return None
    except Exception as e:
        print(f"Error getting cache: {e}")
        return None


def delete_cache(key: str) -> bool:
    """Delete a value from Redis cache"""
    try:
        redis_client.delete(key)
        return True
    except Exception as e:
        print(f"Error deleting cache: {e}")
        return False


def delete_pattern(pattern: str) -> bool:
    """Delete all keys matching a pattern"""
    try:
        keys = redis_client.keys(pattern)
        if keys:
            redis_client.delete(*keys)
        return True
    except Exception as e:
        print(f"Error deleting pattern: {e}")
        return False
