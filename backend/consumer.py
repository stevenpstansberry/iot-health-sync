from confluent_kafka import Consumer
import json
import datetime
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad, pad
import base64
from redis_client import get_redis_connection  
import boto3
import os
from dotenv import load_dotenv
from logger import setup_logger

# Set up logger
logger = setup_logger(name="iot_consumer", log_file="iot_consumer.log")

# Kafka Configuration
KAFKA_BROKER = 'localhost:9092'
KAFKA_TOPIC = 'iot_telemetry'
GROUP_ID = 'iot-consumer-group'

# Load environment variables from .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

conf = {
    'bootstrap.servers': KAFKA_BROKER,
    'group.id': GROUP_ID,
    'auto.offset.reset': 'earliest'
}

consumer = Consumer(conf)
consumer.subscribe([KAFKA_TOPIC])

# S3 Configuration
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
    aws_secret_access_key=os.getenv('AWS_SECRET_KEY')
)
S3_BUCKET_NAME = 'health-data-raw'

# Encryption configuration
encryption_key = bytes.fromhex(os.getenv("ENCRYPTION_KEY"))  # Hex-encoded key

# Get Redis connection from redis_client.py
redis_client = get_redis_connection()

def forward_to_s3(encrypted_data, timestamp, device_id):
    """Send encrypted data to S3."""
    file_name = f"raw_data/{timestamp}_{device_id}.enc"
    try:
        s3_client.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=file_name,
            Body=encrypted_data,
            ContentType='application/octet-stream'
        )
        logger.info(f"Encrypted data forwarded to S3: {file_name}")
    except Exception as e:
        logger.error(f"Error forwarding data to S3: {e}")

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
    try:
        encrypted_bytes = base64.b64decode(encrypted_message)
        iv = encrypted_bytes[:16]  # Extract the IV (first 16 bytes)
        ciphertext = encrypted_bytes[16:]  # The rest is the ciphertext

        cipher = AES.new(encryption_key, AES.MODE_CBC, iv)
        decrypted_data = unpad(cipher.decrypt(ciphertext), AES.block_size).decode('utf-8')
        return decrypted_data
    except Exception as e:
        logger.error(f"Error decrypting message: {e}")
        raise

def process_telemetry(telemetry):
    encrypted_patient_id = encrypt_patient_id(telemetry["patient_id"])
    redis_key = f"anomalies:{encrypted_patient_id}"
    timestamp = datetime.datetime.utcnow().isoformat()

    if telemetry["heart_rate"] > 120:
        logger.critical(f"Very high heart rate detected for {telemetry['patient_name']} ({telemetry['heart_rate']} bpm)")
        field_name = f"high_heart_rate:{timestamp}"
        redis_client.hset(redis_key, field_name, telemetry["heart_rate"])
    elif telemetry["heart_rate"] > 100:
        logger.warning(f"High heart rate detected for {telemetry['patient_name']} ({telemetry['heart_rate']} bpm)")
        field_name = f"high_heart_rate:{timestamp}"
        redis_client.hset(redis_key, field_name, telemetry["heart_rate"])
    elif telemetry["heart_rate"] < 60:
        logger.warning(f"Low heart rate detected for {telemetry['patient_name']} ({telemetry['heart_rate']} bpm)")
        field_name = f"low_heart_rate:{timestamp}"
        redis_client.hset(redis_key, field_name, telemetry["heart_rate"])

    if telemetry["oxygen"] < 85:
        logger.critical(f"Critical oxygen level detected for {telemetry['patient_name']} ({telemetry['oxygen']}%)")
        field_name = f"low_oxygen:{timestamp}"
        redis_client.hset(redis_key, field_name, telemetry["oxygen"])
    elif telemetry["oxygen"] < 90:
        logger.warning(f"Low oxygen level detected for {telemetry['patient_name']} ({telemetry['oxygen']}%)")
        field_name = f"low_oxygen:{timestamp}"
        redis_client.hset(redis_key, field_name, telemetry["oxygen"])

    if telemetry["temperature"] > 38:
        logger.warning(f"Fever detected for {telemetry['patient_name']} ({telemetry['temperature']}°C)")
        field_name = f"fever:{timestamp}"
        redis_client.hset(redis_key, field_name, telemetry["temperature"])
    elif telemetry["temperature"] < 35:
        logger.warning(f"Hypothermia detected for {telemetry['patient_name']} ({telemetry['temperature']}°C)")
        field_name = f"hypothermia:{timestamp}"
        redis_client.hset(redis_key, field_name, telemetry["temperature"])

    redis_client.expire(redis_key, 3600)  # Expire after 1 hour

logger.info(f"Subscribed to Kafka topic: {KAFKA_TOPIC}")

while True:
    msg = consumer.poll(1.0)  # Poll for new messages
    if msg is None:
        continue
    if msg.error():
        logger.error(f"Consumer error: {msg.error()}")
        continue

    try:
        encrypted_message = msg.value().decode('utf-8')
        decrypted_message = decrypt_message(encrypted_message)

        telemetry = json.loads(decrypted_message)
        logger.info(f"Received telemetry from Device ID: {telemetry['device_id']}")

        process_telemetry(telemetry)

        timestamp = datetime.datetime.utcnow().isoformat()
        device_id = telemetry["device_id"]

        forward_to_s3(encrypted_message, timestamp, device_id)
    except Exception as e:
        logger.exception("Error processing message")

consumer.close()
logger.info("Kafka consumer closed.")
