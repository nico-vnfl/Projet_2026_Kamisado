import socket
import json
import struct
import threading
import traceback
from IA import compute_move

HOST = "172.17.10.130" #taper l'IP 
PORT = 3000 
CLIENT_PORT = 1111

#transforme fct en message python: 
def make_packet(message,length_in_bits=False):
    message_data = json.dumps(message).encode()
    message_length = len(message_data)
    if length_in_bits:
        message_length *= 8 #un octet tranformé en 8bit
    return struct.pack("I",message_length) + message_data



def recvall(sock, n):
    data = b""
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data

def send_move(client, move): #envoie le move en reponse
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
                        print(response)

                        resp_data = json.dumps(response).encode()
                        packet = struct.pack("I", len(resp_data)) + resp_data
                        client.sendall(packet)
                        

                    elif msg["request"] == "play":
                        move = compute_move(msg)
                        send_move(client, move)  

                    else:
                        response = {"response" : "Waiting for ping or play"}
                        resp_data = json.dumps(response) .encode()
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
