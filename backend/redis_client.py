import redis
from logger import setup_logger

# Set up logger
logger = setup_logger(name="redis_connection", log_file="redis_connection.log")

def get_redis_connection():
    """
    Returns a Redis client connection and logs success or failure.
    """
    try:
        redis_conn = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)
        if redis_conn.ping():
            logger.info("Connected to Redis successfully!")
        return redis_conn
    except redis.ConnectionError as e:
        logger.error(f"Error connecting to Redis: {e}")
        raise
