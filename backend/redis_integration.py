"""
Redis Integration for ReSonata
Adds caching, session management, and rate limiting to qualify for Redis 10k credits prize
"""

import redis
import json
import os
from functools import wraps

# Initialize Redis connection
try:
    redis_client = redis.Redis(
        host=os.getenv('REDIS_HOST', 'localhost'),
        port=int(os.getenv('REDIS_PORT', 6379)),
        db=0,
        decode_responses=True
    )
    # Test connection
    redis_client.ping()
    REDIS_AVAILABLE = True
except:
    REDIS_AVAILABLE = False
    print("Redis not available, running without cache")


def cache_mistral_response(mood, innovation_level, response_data, ttl=3600):
    """Cache Mistral API response for 1 hour"""
    if not REDIS_AVAILABLE:
        return False
    
    try:
        cache_key = f"mistral:response:{mood}:{innovation_level}"
        redis_client.setex(
            cache_key,
            ttl,
            json.dumps(response_data)
        )
        return True
    except Exception as e:
        print(f"Redis cache error: {e}")
        return False


def get_cached_mistral_response(mood, innovation_level):
    """Get cached Mistral API response"""
    if not REDIS_AVAILABLE:
        return None
    
    try:
        cache_key = f"mistral:response:{mood}:{innovation_level}"
        cached = redis_client.get(cache_key)
        if cached:
            return json.loads(cached)
    except Exception as e:
        print(f"Redis get error: {e}")
    
    return None


def store_user_piece(user_id, piece_data, ttl=86400):
    """Store user-generated piece for 24 hours"""
    if not REDIS_AVAILABLE:
        return False
    
    try:
        piece_key = f"user:piece:{user_id}:{piece_data.get('timestamp')}"
        redis_client.setex(
            piece_key,
            ttl,
            json.dumps(piece_data)
        )
        # Add to user's piece list
        list_key = f"user:pieces:{user_id}"
        redis_client.lpush(list_key, piece_key)
        redis_client.expire(list_key, ttl)
        return True
    except Exception as e:
        print(f"Redis store error: {e}")
        return False


def get_user_pieces(user_id, limit=10):
    """Get user's recent pieces"""
    if not REDIS_AVAILABLE:
        return []
    
    try:
        list_key = f"user:pieces:{user_id}"
        piece_keys = redis_client.lrange(list_key, 0, limit - 1)
        
        pieces = []
        for key in piece_keys:
            piece_data = redis_client.get(key)
            if piece_data:
                pieces.append(json.loads(piece_data))
        
        return pieces
    except Exception as e:
        print(f"Redis get pieces error: {e}")
        return []


def rate_limit(key, max_requests=10, window=60):
    """Rate limiting: max_requests per window seconds"""
    if not REDIS_AVAILABLE:
        return True  # Allow if Redis unavailable
    
    try:
        rate_key = f"rate_limit:{key}"
        current = redis_client.incr(rate_key)
        
        if current == 1:
            redis_client.expire(rate_key, window)
        
        return current <= max_requests
    except Exception as e:
        print(f"Rate limit error: {e}")
        return True  # Fail open


def get_analytics():
    """Get usage analytics"""
    if not REDIS_AVAILABLE:
        return {}
    
    try:
        total_generations = redis_client.get("stats:total_generations") or 0
        total_users = redis_client.scard("stats:users") or 0
        cache_hits = redis_client.get("stats:cache_hits") or 0
        
        return {
            "total_generations": int(total_generations),
            "total_users": int(total_users),
            "cache_hits": int(cache_hits),
            "redis_available": True
        }
    except Exception as e:
        print(f"Analytics error: {e}")
        return {"redis_available": False}


def increment_stat(stat_name):
    """Increment a statistic counter"""
    if not REDIS_AVAILABLE:
        return
    
    try:
        redis_client.incr(f"stats:{stat_name}")
    except:
        pass

