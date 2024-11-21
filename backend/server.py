import socket
from confluent_kafka import Producer
import json
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

# Encryption configuration
encryption_key = bytes.fromhex("63663255767434797a59587252423657697151594131474749705a4766387644")  # Hex-encoded key

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

            # Debug encrypted values
            print("IV (Raw):", iv)
            print("Encrypted Data (Base64):", encrypted_data)

            # Decrypt the data
            cipher = AES.new(encryption_key, AES.MODE_CBC, iv)
            decrypted_data = unpad(cipher.decrypt(encrypted_bytes), AES.block_size).decode('utf-8')
            print("Decrypted Data (Raw):", decrypted_data)

            telemetry = json.loads(decrypted_data)

            # Print decrypted telemetry data
            print("Received Decrypted Data:", telemetry)

            # Forward to Kafka
            try:
                producer.produce(
                    KAFKA_TOPIC,
                    key=str(telemetry.get('device_id', 'unknown')),
                    value=json.dumps(telemetry)
                )
                producer.flush()  # Ensure the message is delivered
                print("Sent to Kafka:", telemetry)
            except Exception as e:
                print("Failed to send to Kafka:", e)

        except Exception as e:
            print("Decryption Error:", e)

    client.close()
