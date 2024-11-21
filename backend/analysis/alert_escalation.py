import redis_client

def alert_escalation(threshold=10):
    redis_conn = redis_client.get_redis_connection()
    keys = redis_conn.keys("anomalies:*")

    for key in keys:
        # Count the total number of anomalies (number of fields in the hash)
        total_alerts = len(redis_conn.hkeys(key))
        if total_alerts > threshold:
            print(f"Escalation Alert: Patient {key.split(':')[1]} has {total_alerts} anomalies!")
