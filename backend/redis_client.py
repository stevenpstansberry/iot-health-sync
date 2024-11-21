import redis
import json

# Connect to Redis
redis_client = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)

# Test connection
if redis_client.ping():
    print("Connected to Redis!")

# Function to process telemetry and store anomalies
def process_telemetry(telemetry):
    patient_id = telemetry["patient_id"]

    # Key for this patient's anomalies
    key = f"anomalies:{patient_id}"

    # Check and store anomalies
    if telemetry["heart_rate"] > 100:
        redis_client.hincrby(key, "high_heart_rate", 1)
        print(f"ALERT: High heart rate for patient {patient_id}!")
        
    if telemetry["oxygen"] < 90:
        redis_client.hincrby(key, "low_oxygen", 1)
        print(f"ALERT: Low oxygen level for patient {patient_id}!")
        
    if telemetry["temperature"] > 38:
        redis_client.hincrby(key, "fever", 1)
        print(f"ALERT: Fever for patient {patient_id}!")
        
    # Add TTL to anomalies key to clear old data automatically
    redis_client.expire(key, 3600)  # Expire after 1 hour

# Example telemetry data
telemetry_data = [
    {"patient_id": "100234567890", "heart_rate": 105, "oxygen": 95, "temperature": 37},
    {"patient_id": "200345678901", "heart_rate": 75, "oxygen": 85, "temperature": 36},
    {"patient_id": "300456789012", "heart_rate": 65, "oxygen": 92, "temperature": 39},
    {"patient_id": "100234567890", "heart_rate": 110, "oxygen": 93, "temperature": 36},
    {"patient_id": "200345678901", "heart_rate": 80, "oxygen": 88, "temperature": 36},
]

# Process each telemetry record
for telemetry in telemetry_data:
    process_telemetry(telemetry)

# Retrieve and print anomaly counts for each patient
patient_ids = {data["patient_id"] for data in telemetry_data}  # Get unique patient IDs

for patient_id in patient_ids:
    key = f"anomalies:{patient_id}"
    patient_anomalies = redis_client.hgetall(key)

    print(f"\nAnomalies for patient {patient_id}:")
    for category, count in patient_anomalies.items():
        print(f"  {category}: {count}")
