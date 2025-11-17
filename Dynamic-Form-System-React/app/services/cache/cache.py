import redis
import json
import os
from typing import Optional, Dict, Any


# Initialize Redis connection
redis_url = os.getenv("REDIS_URL", "redis://redis:6379")
try:
    r = redis.from_url(redis_url, decode_responses=True)
    r.ping()
    print("✅ Redis connected successfully")
except Exception as e:
    print(f"⚠️ Redis connection failed: {e} - Cache disabled")
    r = None


def cache_get(key: str) -> Optional[Dict[str, Any]]:

    if not r:
        return None
    
    try:
        data = r.get(key)
        return json.loads(data) if data else None
    except Exception as e:
        print(f"⚠️ Cache GET error for {key}: {e}")
        return None


def cache_set(key: str, value: Dict[str, Any], ttl: int = 3600) -> bool:

    if not r:
        return False
    
    try:
        r.setex(key, ttl, json.dumps(value))
        return True
    except Exception as e:
        print(f"⚠️ Cache SET error for {key}: {e}")
        return False


def cache_delete(key: str) -> bool:
    if not r:
        return False
    
    try:
        result = r.delete(key)
        return result > 0
    except Exception as e:
        print(f"⚠️ Cache DELETE error for {key}: {e}")
        return False


def cache_delete_pattern(pattern: str) -> int:
    if not r:
        return 0
    
    try:
        deleted_count = 0
        # Use SCAN to iterate keys (doesn't block)
        for key in r.scan_iter(match=pattern):
            r.delete(key)
            deleted_count += 1
        return deleted_count
    except Exception as e:
        print(f"⚠️ Cache DELETE PATTERN error for {pattern}: {e}")
        return 0


def cache_clear() -> bool:
    if not r:
        return False
    
    try:
        r.flushdb()
        return True
    except Exception as e:
        print(f"⚠️ Cache CLEAR error: {e}")
        return False