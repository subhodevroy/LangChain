import os
import redis
client =redis.Redis.from_url(
    os.environ["REDIS_URL"],
    decode_responses=True
)