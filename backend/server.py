import socket
from confluent_kafka import Producer
import json

# Configure Kafka
KAFKA_BROKER = 'localhost:9092'
KAFKA_TOPIC = 'iot_telemetry'

conf = {
    'bootstrap.servers': KAFKA_BROKER,
    'client.id': 'iot-server'
}
producer = Producer(conf)

# Configure server
HOST = '127.0.0.1'
PORT = 9999

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(1)

print(f"Server listening on {HOST}:{PORT}...")

while True:
    client, addr = server.accept()
    data = client.recv(1024).decode('utf-8')
    if data:
        telemetry = json.loads(data)
        print("Received:", telemetry)

        # Forward to Kafka
        try:
            producer.produce(KAFKA_TOPIC, key=str(telemetry.get('device_id', 'unknown')), value=json.dumps(telemetry))
            producer.flush()  # Ensure the message is delivered
            print("Sent to Kafka:", telemetry)
        except Exception as e:
            print("Failed to send to Kafka:", e)

    client.close()
