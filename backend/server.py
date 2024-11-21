import socket

# Configure server
HOST = '127.0.0.1'
PORT = 9999

# Start listening
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(1)

print(f"Server listening on {HOST}:{PORT}...")

while True:
    client, addr = server.accept()
    data = client.recv(1024).decode('utf-8')
    if data:
        print("Received:", data)
    client.close()
