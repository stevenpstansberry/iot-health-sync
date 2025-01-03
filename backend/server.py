import socket
from confluent_kafka import Producer
import json
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
from datetime import datetime, timezone
import uuid
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv(dotenv_path='../.env')

# Encryption configuration
encryption_key = bytes.fromhex(os.getenv("ENCRYPTION_KEY"))  # Hex-encoded key

# Kafka Configuration
KAFKA_BROKER = 'localhost:9092'
KAFKA_TOPIC = 'iot_telemetry'

conf = {
    'bootstrap.servers': KAFKA_BROKER,
    'client.id': 'iot-server'
}
producer = Producer(conf)

# Server Configuration
HOST = '127.0.0.1'
PORT = 9999

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(1)

print(f"Server listening on {HOST}:{PORT}...")

while True:
    client, addr = server.accept()
    combined_data = client.recv(1024).decode('utf-8')
    if combined_data:
        try:
            # Split the IV and encrypted data
            iv, encrypted_data = combined_data.split(":")
            iv = bytes.fromhex(iv)  # Convert IV back to bytes
            encrypted_bytes = base64.b64decode(encrypted_data)

            # Decrypt the data
            cipher = AES.new(encryption_key, AES.MODE_CBC, iv)
            decrypted_data = unpad(cipher.decrypt(encrypted_bytes), AES.block_size).decode('utf-8')
            telemetry = json.loads(decrypted_data)

            # Add metadata
            telemetry["processing_timestamp"] = datetime.now(timezone.utc).isoformat()
            telemetry["server_id"] = "iot-server-01"
            telemetry["encryption_version"] = "AES-256-CBC-v1"
            telemetry["message_id"] = telemetry.get("message_id", str(uuid.uuid4()))

            # Re-encrypt the data for Kafka
            new_iv = get_random_bytes(16)  # Generate a new random IV
            new_cipher = AES.new(encryption_key, AES.MODE_CBC, new_iv)
            payload = {**telemetry}  # Combine telemetry and metadata
            encrypted_for_kafka = base64.b64encode(
                new_iv + new_cipher.encrypt(pad(json.dumps(payload).encode('utf-8'), AES.block_size))
            )

            # Forward encrypted data to Kafka
            producer.produce(
                KAFKA_TOPIC,
                key=str(telemetry["device_id"]),
                value=encrypted_for_kafka.decode('utf-8')
            )
            producer.flush()  # Ensure the message is delivered
            print("Sent Encrypted Data to Kafka:", encrypted_for_kafka.decode('utf-8'))

        except Exception as e:
            print("Decryption or Encryption Error:", e)

    client.close()