from confluent_kafka import Consumer
import json
import datetime
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad, pad
import base64
from redis_client import get_redis_connection  

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
encryption_key = bytes.fromhex("63663255767434797a59587252423657697151594131474749705a4766387644")  # 32 bytes (256-bit key)

# Get Redis connection from redis_client.py
redis_client = get_redis_connection()

# Encryption and Decryption Utilities
def encrypt_patient_id(patient_id):
    cipher = AES.new(encryption_key, AES.MODE_ECB)
    padded_id = pad(patient_id.encode('utf-8'), AES.block_size)
    encrypted_bytes = cipher.encrypt(padded_id)
    return base64.b64encode(encrypted_bytes).decode('utf-8')

def decrypt_patient_id(encrypted_id):
    cipher = AES.new(encryption_key, AES.MODE_ECB)
    encrypted_bytes = base64.b64decode(encrypted_id)
    decrypted_id = unpad(cipher.decrypt(encrypted_bytes), AES.block_size)
    return decrypted_id.decode('utf-8')

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
    # Encrypt the patient ID
    encrypted_patient_id = encrypt_patient_id(telemetry["patient_id"])
    redis_key = f"anomalies:{encrypted_patient_id}"

    # Current timestamp in ISO 8601 format
    timestamp = datetime.datetime.utcnow().isoformat()

    # Alerts based on telemetry data
    if telemetry["heart_rate"] > 120:
        print(f"CRITICAL ALERT: Very high heart rate detected for {telemetry['patient_name']}! ({telemetry['heart_rate']} bpm)")
        field_name = f"high_heart_rate:{timestamp}"
        redis_client.hset(redis_key, field_name, telemetry["heart_rate"])
    elif telemetry["heart_rate"] > 100:
        print(f"ALERT: High heart rate detected for {telemetry['patient_name']} ({telemetry['heart_rate']} bpm)!")
        field_name = f"high_heart_rate:{timestamp}"
        redis_client.hset(redis_key, field_name, telemetry["heart_rate"])
    elif telemetry["heart_rate"] < 60:
        print(f"ALERT: Low heart rate detected for {telemetry['patient_name']} ({telemetry['heart_rate']} bpm)!")
        field_name = f"low_heart_rate:{timestamp}"
        redis_client.hset(redis_key, field_name, telemetry["heart_rate"])

    if telemetry["oxygen"] < 85:
        print(f"CRITICAL ALERT: Critical oxygen level detected for {telemetry['patient_name']}! ({telemetry['oxygen']}%)")
        field_name = f"low_oxygen:{timestamp}"
        redis_client.hset(redis_key, field_name, telemetry["oxygen"])
    elif telemetry["oxygen"] < 90:
        print(f"ALERT: Low oxygen level detected for {telemetry['patient_name']} ({telemetry['oxygen']}%)!")
        field_name = f"low_oxygen:{timestamp}"
        redis_client.hset(redis_key, field_name, telemetry["oxygen"])

    if telemetry["temperature"] > 38:
        print(f"ALERT: Fever detected for {telemetry['patient_name']}! ({telemetry['temperature']}°C)")
        field_name = f"fever:{timestamp}"
        redis_client.hset(redis_key, field_name, telemetry["temperature"])
    elif telemetry["temperature"] < 35:
        print(f"ALERT: Hypothermia detected for {telemetry['patient_name']}! ({telemetry['temperature']}°C)")
        field_name = f"hypothermia:{timestamp}"
        redis_client.hset(redis_key, field_name, telemetry["temperature"])

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
