import time
import os
import redis.asyncio as redis
from fastapi import Request, HTTPException


REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client = redis.from_url(REDIS_URL, decode_responses=True)


RATE_LIMITS = {
    "anonymous": (2, 60), 
    "authenticated": (10, 60), 
}


async def rate_limit(request: Request, user_id: str | None = None):
  
    identity = user_id or request.client.host
    limit_type = "authenticated" if user_id else "anonymous"
    limit, period = RATE_LIMITS[limit_type]

    key = f"rate_limit:{limit_type}:{identity}"
    now = int(time.time())
    window_start = now - period

    
    await redis_client.zremrangebyscore(key, min=0, max=window_start)

  
    request_count = await redis_client.zcard(key)

   
    if request_count >= limit:
        raise HTTPException(status_code=429, detail="Too many requests")


    await redis_client.zadd(key, {str(now): now})


    await redis_client.expire(key, period)
