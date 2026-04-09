import socket
import json
import struct
import threading

HOST = "172.17.89.143"
PORT = 3000

CLIENT_PORT = 8888



def start_server():
    def handler():
        with socket.socket() as s:
            s.bind(("0.0.0.0", CLIENT_PORT))
            s.listen()

            print("Serveur local lancé sur 8888")

            while True:
                client, addr = s.accept()
                with client:
                    
                    raw_len = client.recv(4)
                    msg_len = struct.unpack("!I", raw_len)[0]

                    data = client.recv(msg_len)
                    msg = json.loads(data.decode())

                    print("\n[RECU DU SERVEUR]", msg)

                    
                    if msg["request"] == "ping":
                        response = {"response": "pong"}
                        resp_data = json.dumps(response).encode()
                        packet = struct.pack("!I", len(resp_data)) + resp_data
                        client.sendall(packet)

    threading.Thread(target=handler, daemon=True).start()



start_server()



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

print("INSCRIPTION ENVOYÉE")



while True:
    pass