from confluent_kafka import Consumer
import redis
import json
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import base64

# Kafka Configuration
KAFKA_BROKER = 'localhost:9092'
KAFKA_TOPIC = 'iot_telemetry'
GROUP_ID = 'iot-consumer-group'

conf = {
    'bootstrap.servers': KAFKA_BROKER,
    'group.id': GROUP_ID,
    'auto.offset.reset': 'earliest'
}

consumer = Consumer(conf)
consumer.subscribe([KAFKA_TOPIC])

# Encryption configuration
encryption_key = bytes.fromhex("63663255767434797a59587252423657697151594131474749705a4766387644")  # Hex-encoded key

# Redis Configuration
redis_client = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)

# Test Redis connection
if redis_client.ping():
    print("Connected to Redis!")

def decrypt_message(encrypted_message):
    # Decode Base64 message
    encrypted_bytes = base64.b64decode(encrypted_message)
    iv = encrypted_bytes[:16]  # Extract the IV (first 16 bytes)
    ciphertext = encrypted_bytes[16:]  # The rest is the ciphertext

    # Decrypt using AES
    cipher = AES.new(encryption_key, AES.MODE_CBC, iv)
    decrypted_data = unpad(cipher.decrypt(ciphertext), AES.block_size).decode('utf-8')
    return decrypted_data

def process_telemetry(telemetry):
    # Key for this patient's anomalies
    patient_id = telemetry["patient_id"]
    redis_key = f"anomalies:{patient_id}"

    # Alerts based on telemetry data
    if telemetry["heart_rate"] > 120:
        print(f"CRITICAL ALERT: Very high heart rate detected for {telemetry['patient_name']}! ({telemetry['heart_rate']} bpm)")
        redis_client.hincrby(redis_key, "high_heart_rate", 1)
        redis_client.rpush(redis_key + ":details", json.dumps({"type": "high_heart_rate", "value": telemetry["heart_rate"]}))
    elif telemetry["heart_rate"] > 100:
        print(f"ALERT: High heart rate detected for {telemetry['patient_name']} ({telemetry['heart_rate']} bpm)!")
        redis_client.hincrby(redis_key, "high_heart_rate", 1)
        redis_client.rpush(redis_key + ":details", json.dumps({"type": "high_heart_rate", "value": telemetry["heart_rate"]}))
    elif telemetry["heart_rate"] < 60:
        print(f"ALERT: Low heart rate detected for {telemetry['patient_name']} ({telemetry['heart_rate']} bpm)!")
        redis_client.hincrby(redis_key, "low_heart_rate", 1)
        redis_client.rpush(redis_key + ":details", json.dumps({"type": "low_heart_rate", "value": telemetry["heart_rate"]}))

    if telemetry["oxygen"] < 85:
        print(f"CRITICAL ALERT: Critical oxygen level detected for {telemetry['patient_name']}! ({telemetry['oxygen']}%)")
        redis_client.hincrby(redis_key, "low_oxygen", 1)
        redis_client.rpush(redis_key + ":details", json.dumps({"type": "low_oxygen", "value": telemetry["oxygen"]}))
    elif telemetry["oxygen"] < 90:
        print(f"ALERT: Low oxygen level detected for {telemetry['patient_name']} ({telemetry['oxygen']}%)!")
        redis_client.hincrby(redis_key, "low_oxygen", 1)
        redis_client.rpush(redis_key + ":details", json.dumps({"type": "low_oxygen", "value": telemetry["oxygen"]}))

    if telemetry["temperature"] > 38:
        print(f"ALERT: Fever detected for {telemetry['patient_name']}! ({telemetry['temperature']}°C)")
        redis_client.hincrby(redis_key, "fever", 1)
        redis_client.rpush(redis_key + ":details", json.dumps({"type": "fever", "value": telemetry["temperature"]}))
    elif telemetry["temperature"] < 35:
        print(f"ALERT: Hypothermia detected for {telemetry['patient_name']}! ({telemetry['temperature']}°C)")
        redis_client.hincrby(redis_key, "hypothermia", 1)
        redis_client.rpush(redis_key + ":details", json.dumps({"type": "hypothermia", "value": telemetry["temperature"]}))

    # Optional: Set TTL to automatically remove old data
    redis_client.expire(redis_key, 3600)  # Expire after 1 hour

print(f"Subscribed to Kafka topic: {KAFKA_TOPIC}")

while True:
    msg = consumer.poll(1.0)  # Poll for new messages
    if msg is None:
        continue
    if msg.error():
        print(f"Consumer error: {msg.error()}")
        continue

    try:
        # Decrypt the message
        encrypted_message = msg.value().decode('utf-8')
        decrypted_message = decrypt_message(encrypted_message)

        # Parse the JSON data
        telemetry = json.loads(decrypted_message)
        print(f"Received telemetry from (Device ID: {telemetry['device_id']})")

        # Process the telemetry data for alerts and forward to Redis
        process_telemetry(telemetry)

    except Exception as e:
        print("Error processing message:", e)

consumer.close()
