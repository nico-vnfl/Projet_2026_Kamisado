import socket
import json
import struct
import threading

HOST = "172.17.89.143"
PORT = 3000
CLIENT_PORT = 8888


def recvall(sock, n):
    data = b""
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data


def start_server():
    def handler():
        with socket.socket() as s:
            s.bind(("0.0.0.0", CLIENT_PORT))
            s.listen()

            print("Serveur local lancé sur 8888")

            while True:
                client, addr = s.accept()
                with client:

                    raw_len = recvall(client, 4)
                    if not raw_len:
                        continue

                    msg_len = struct.unpack("I", raw_len)[0]

                    data = recvall(client, msg_len)
                    if not data:
                        continue

                    msg = json.loads(data.decode())

                    print("[RECU DU SERVEUR]", msg)

                    if msg["request"] == "ping":
                        response = {"response": "pong"}

                        resp_data = json.dumps(response).encode()
                        packet = struct.pack("I", len(resp_data)) + resp_data

                        client.sendall(packet)

    thread = threading.Thread(target=handler, daemon=True)
    thread.start()


def subscribe():
    msg = {
        "request": "subscribe",
        "port": CLIENT_PORT,
        "name": "Theo",
        "matricules": ["12345"]
    }

    data = json.dumps(msg).encode()
    packet = struct.pack("I", len(data)) + data

    with socket.socket() as s:
        s.connect((HOST, PORT))
        s.sendall(packet)

    print("INSCRIPTION ENVOYEE")


# Lancement
start_server()
subscribe()

# Boucle pour garder le programme actif
while True:
    pass