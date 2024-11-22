import redis

def get_redis_connection():
    """
    Returns a Redis client connection and logs success.
    """
    try:
        redis_conn = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)
        if redis_conn.ping():
            print("Connected to Redis successfully!")
        return redis_conn
    except redis.ConnectionError as e:
        print(f"Error connecting to Redis: {e}")
        raise
