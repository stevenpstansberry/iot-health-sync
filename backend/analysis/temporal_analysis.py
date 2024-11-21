import redis_client
from collections import defaultdict

def temporal_analysis():
    redis_conn = redis_client.get_redis_connection()
    keys = redis_conn.keys("anomalies:*")
    hourly_stats = defaultdict(int)

    for key in keys:
        patient_data = redis_conn.hgetall(key)
        for field in patient_data.keys():
            timestamp = field.split(":")[1]  # Extract timestamp
            hour = timestamp.split("T")[1][:2]  # Extract the hour
            hourly_stats[hour] += 1

    print("Hourly Anomaly Frequency:")
    for hour, count in sorted(hourly_stats.items()):
        print(f"  {hour}:00 - {count} anomalies")
