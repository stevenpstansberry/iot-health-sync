import redis_client

def priority_patient_list():
    redis_conn = redis_client.get_redis_connection()
    keys = redis_conn.keys("anomalies:*")
    patient_alerts = []

    for key in keys:
        # Total anomalies is the count of fields in the hash
        total_alerts = len(redis_conn.hkeys(key))
        patient_alerts.append((key.split(":")[1], total_alerts))  # Extract patient ID

    # Sort by total alerts
    patient_alerts.sort(key=lambda x: x[1], reverse=True)

    print("Priority Patient List:")
    for patient_id, alert_count in patient_alerts:
        print(f"  Patient {patient_id}: {alert_count} alerts")
