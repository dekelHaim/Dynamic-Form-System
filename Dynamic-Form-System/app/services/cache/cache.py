import redis
import json
import os
from typing import Optional, Dict, Any


redis_url = os.getenv("REDIS_URL", "redis://redis:6379")

try:
    r = redis.from_url(redis_url, decode_responses=True)
    r.ping()
except Exception:
    r = None 


def cache_get(key: str) -> Optional[Dict[str, Any]]:
    """Get from cache - Simple, fast"""
    if not r:
        return None
    try:
        data = r.get(key)
        return json.loads(data) if data else None
    except Exception:
        return None

def cache_set(key: str, value: Dict[str, Any], ttl: int = 3600):
    """Set cache with 1 hour TTL - Simple"""
    if not r:
        return
    try:
        r.setex(key, ttl, json.dumps(value))
    except Exception:
        pass

def cache_delete(key: str):
    """Delete specific cache key"""
    if not r:
        return
    try:
        r.delete(key)
    except Exception:
        pass

def cache_delete_pattern(pattern: str):
    """Delete all keys matching pattern - For invalidation"""
    if not r:
        return 0
    try:
        count = 0
        for key in r.scan_iter(match=pattern):
            r.delete(key)
            count += 1
        return count
    except Exception:
        return 0

def cache_clear():
    """Clear entire cache"""
    if not r:
        return
    try:
        r.flushdb()
    except Exception:
        pass