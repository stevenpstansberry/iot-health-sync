import redis_client
from collections import Counter

def population_insights():
    redis_conn = redis_client.get_redis_connection()
    keys = redis_conn.keys("anomalies:*")
    aggregate_stats = Counter()

    for key in keys:
        patient_data = redis_conn.hgetall(key)
        for field, _ in patient_data.items():
            anomaly_type = field.split(":")[0]  # Extract anomaly type (ignore timestamp)
            aggregate_stats[anomaly_type] += 1

    print("Population-Level Insights:")
    for anomaly, total in aggregate_stats.items():
        print(f"  {anomaly}: {total} occurrences")
