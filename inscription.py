import socket
import json
import struct
import threading
import traceback
from IA import compute_move

HOST = "198.168.1.&" #taper l'IP 
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

def receive_message(sock):
    len_brute = recvall(sock, 4)
    if not len_brute:
        return None
    
    len_prevu = struct.unpack("I", len_brute)[0]
    data = b""

    while len(data) < len_prevu:
        try:
            packet = sock.recv(len_prevu - len(data))
        except TimeoutError:
            break
        if not packet:
            break
        data += packet

        try:
            return json.loads(data.decode())
        except json.JSONDecodeError:
            pass
    if len_prevu % 8 == 0 and len(data) >= len_prevu // 8:
        return json.loads(data[0 : len_prevu // 8].decode())

    if data:
        return json.loads(data.decode())
    
    return None





def send_move(client, move): #envoie le move en reponse
    if not isinstance(move,list): 
        print("[COUP INVALIDE]",move)
        move = [(0,0)], [(0,0)]

    response = {
        "response":"move",
        "move": move
    }

    
    client.sendall(make_packet(response))

    print("[COUP ENVOYE]", response)


def start_server(): 
    def handler():
        with socket.socket() as s:
            s.bind(("0.0.0.0", CLIENT_PORT))
            s.listen()

            print(f"Serveur local lancé sur {CLIENT_PORT}")

            while True:
                client, addr = s.accept()
                with client:
                    try:
                        client.settimeout(2)
                        print("[CONNEXION]", addr)
                        msg = receive_message(client)
                        if not msg: 
                            print("[allo Huston ici la terre???]")
                            continue
                        print("[SERVEUR:]", msg)



                        if msg["request"] == "ping":
                            response = {"response": "pong"}
                            print(response)
                            client.sendall(make_packet(response))
                        

                        elif msg["request"] == "play":
                            move = compute_move(msg)
                            send_move(client, move)  

                        else:
                            response = {"response" : "Waiting for ping or play"}
                            client.sendall(make_packet(response))
                    except Exception:
                        print("[c'est pas ma faute c'est le serveur]")
                        traceback.print_exc()

    thread = threading.Thread(target=handler, daemon=True)
    thread.start()

def subscribe_msg():
    return {
        "request": "subscribe",
        "port": CLIENT_PORT,
        "name": "LIB",
        "matricules": ["24355"]
    }

def subscribe():
    msg = subscribe_msg()
    with socket.socket() as s:
        s.connect((HOST, PORT))
        s.sendall(make_packet(msg))

    print("INSCRIPTION ENVOYEE")
    return msg
