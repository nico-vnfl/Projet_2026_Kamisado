import socket
import json
import struct
import threading

HOST = "172.17.10.130" #taper l'IP 
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

def compute_move(state):
    board = state["board"]
    color = state["color"]

    for l in range(8):
        for c in range(8):
            case = board[l][c]
            if case and case["player"] == 1 and case["color"] == color:
                from_l, from_c = l, c
    
    to_l = from_l - 1
    to_c = from_c

    if 0 <= to_l < 8 and board[to_l][to_c] is None:
        return [[from_l, from_c], [to_l, to_c]]
    
    return [[from_l, from_c], [from_l, from_c]]

def send_move(client, move):
    response = {
        "response":"move",
        "move": move
    }

    response_data = json.dumps(response).encode()
    packet = struct.pack("I", len(response_data)) + response_data
    client.sendall(packet)

    print("[COUP ENVOYE]", move)

    
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

def subscribe_msg():
    return {
        "request": "subscribe",
        "port": CLIENT_PORT,
        "name": "Nico",
        "matricules": ["24350"]
    }

def subscribe():
    msg = subscribe_msg()
    data = json.dumps(msg).encode()
    packet = struct.pack("I", len(data)) + data

    with socket.socket() as s:
        s.connect((HOST, PORT))
        s.sendall(packet)

    print("INSCRIPTION ENVOYEE")
    return msg


# Lancement
if __name__ == "__main__":

    start_server()
    subscribe()

# Boucle pour garder le programme actif
while True:
    pass