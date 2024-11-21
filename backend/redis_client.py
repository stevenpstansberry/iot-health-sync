import redis

# Connect to Redis
redis_client = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)

# Test connection
print(redis_client.ping())  
