import socket
import pytest

from moves import tile_color, piece, player_direction, generate_moves
from IA import choix_move, compute_move, move_secours
from inscription import (
    make_packet,
    subscribe_msg,
    recvall,
    receive_message,
    send_move,
    subscribe,
    start_server,
    CLIENT_PORT,
    HOST,
    PORT
)


def get_empty_board():
    return [[["red", None] for _ in range(8)] for _ in range(8)]


def test_tile_and_piece():
    case = ["orange", ["blue", "dark"]]

    assert tile_color(case) == "orange"
    assert piece(case) == ["blue", "dark"]


def test_player_direction():
    assert player_direction(0) == -1
    assert player_direction(1) == 1


def test_generate_moves_simple_forward():
    board = get_empty_board()
    board[6][3] = ["red", ["blue", "dark"]]

    moves = generate_moves(board, None, 0)

    assert [[6, 3], [5, 3]] in moves
    assert [[6, 3], [4, 3]] in moves


def test_generate_moves_bloque():
    board = get_empty_board()
    board[6][3] = ["red", ["blue", "dark"]]
    board[5][3] = ["red", ["yellow", "light"]]

    moves = generate_moves(board, None, 0)

    assert [[6, 3], [5, 3]] not in moves


def test_generate_moves_forced_color():
    board = get_empty_board()
    board[6][3] = ["red", ["blue", "dark"]]
    board[6][4] = ["red", ["yellow", "dark"]]

    moves = generate_moves(board, "blue", 0)

    for move in moves:
        assert move[0] == [6, 3]


def test_choose_move_prefers_forward():
    moves = [
        [[6, 3], [5, 3]],
        [[6, 3], [4, 3]],
    ]

    assert choix_move(moves, 0) == [[6, 3], [4, 3]]


def test_compute_move_cree_un_move():
    board = get_empty_board()
    board[6][3] = ["red", ["blue", "dark"]]

    msg = {
        "state": {
            "board": board,
            "current": 0,
            "color": None,
        }
    }

    assert compute_move(msg) is not None


def test_compute_move_secours():
    board = get_empty_board()
    board[6][2] = ["red", ["blue", "dark"]]

    msg = {
        "state": {
            "board": board,
            "current": 0,
            "color": "green",
        }
    }

    assert compute_move(msg) == [[6, 2], [5, 2]]


def test_move_secours_retourne_zero_si_bloque():
    board = get_empty_board()
    board[6][2] = ["red", ["blue", "dark"]]
    board[5][2] = ["red", ["yellow", "light"]]

    assert move_secours(board, 0) == [[0, 0], [0, 0]]


def test_make_packet():
    packet = make_packet({"response": "pong"})

    assert isinstance(packet, bytes)
    assert len(packet) > 4


def test_make_packet_en_bits():
    packet = make_packet({"response": "pong"}, True)

    taille = int.from_bytes(packet[:4], "little")

    assert taille == len(packet[4:]) * 8


def test_recvall_recoit_tout():
    serveur, client = socket.socketpair()

    try:
        client.sendall(b"abcd")

        assert recvall(serveur, 4) == b"abcd"
    finally:
        serveur.close()
        client.close()


def test_recvall_retourne_none_si_socket_coupe():
    serveur, client = socket.socketpair()

    try:
        client.sendall(b"ab")
        client.close()

        assert recvall(serveur, 4) is None
    finally:
        serveur.close()


def test_receive_message_simple():
    serveur, client = socket.socketpair()

    try:
        client.sendall(make_packet({"request": "ping"}))

        assert receive_message(serveur) == {"request": "ping"}
    finally:
        serveur.close()
        client.close()


def test_receive_message_longueur_en_bits():
    serveur, client = socket.socketpair()

    try:
        client.sendall(make_packet({"request": "ping"}, True))

        assert receive_message(serveur) == {"request": "ping"}
    finally:
        serveur.close()
        client.close()


def test_receive_message_none_si_pas_de_taille():
    serveur, client = socket.socketpair()

    try:
        client.close()

        assert receive_message(serveur) is None
    finally:
        serveur.close()


def test_receive_message_incomplet():
    serveur, client = socket.socketpair()

    try:
        client.sendall((5).to_bytes(4, "little"))
        client.sendall(b"abc")
        client.close()

        with pytest.raises(Exception):
            receive_message(serveur)
    finally:
        serveur.close()


def test_send_move_envoie_la_reponse():
    serveur, client = socket.socketpair()

    try:
        send_move(client, [[6, 3], [5, 3]])
        data = serveur.recv(1024)

        assert b'"response": "move"' in data
    finally:
        serveur.close()
        client.close()


def test_send_move_corrige_un_move_invalide():
    serveur, client = socket.socketpair()

    try:
        send_move(client, "pas bon")
        data = serveur.recv(1024)

        assert b'"move"' in data
    finally:
        serveur.close()
        client.close()


def test_subscribe_envoie_le_message(monkeypatch):
    class SocketTest:
        def __init__(self):
            self.adresse = None
            self.envoye = []

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def connect(self, adresse):
            self.adresse = adresse

        def sendall(self, data):
            self.envoye.append(data)

    client = SocketTest()

    monkeypatch.setattr("inscription.socket.socket", lambda: client)

    msg = subscribe()

    assert msg["request"] == "subscribe"
    assert client.adresse == (HOST, PORT)
    assert len(client.envoye) == 1


def test_start_server_lance_un_thread(monkeypatch):
    threads = []

    class ThreadTest:
        def __init__(self, target=None, daemon=None):
            self.target = target
            self.daemon = daemon
            self.started = False

        def start(self):
            self.started = True

    def creer_thread(target=None, daemon=None):
        thread = ThreadTest(target, daemon)
        threads.append(thread)
        return thread

    monkeypatch.setattr("inscription.threading.Thread", creer_thread)

    start_server()

    assert len(threads) == 1
    assert threads[0].daemon is True
    assert threads[0].started is True


def test_start_server_repond_au_ping(monkeypatch):
    class ClientTest:
        def __init__(self):
            self.timeout = None
            self.envoye = []

        def __enter__(self):   
            return self

        def __exit__(self, exc_type, exc, tb):  
            return False

        def settimeout(self, valeur):
            self.timeout = valeur

        def sendall(self, data):
            self.envoye.append(data)

    class ServeurTest:
        def __init__(self):
            self.client = ClientTest()
            self.bind_data = None
            self.listen_fait = False
            self.accept_deja_fait = False

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def bind(self, data):
            self.bind_data = data

        def listen(self):
            self.listen_fait = True

        def accept(self):
            if not self.accept_deja_fait:
                self.accept_deja_fait = True
                return self.client, ("0.0.0.0", CLIENT_PORT)

            raise RuntimeError("stop")

    class ThreadTest:
        def __init__(self, target=None, daemon=None):
            self.target = target
            self.daemon = daemon

        def start(self):
            try:
                self.target()
            except RuntimeError:
                pass

    serveur = ServeurTest()

    monkeypatch.setattr("inscription.socket.socket", lambda: serveur)
    monkeypatch.setattr("inscription.receive_message", lambda client: {"request": "ping"})
    monkeypatch.setattr("inscription.threading.Thread", ThreadTest)

    start_server()

    assert serveur.bind_data == ("0.0.0.0", CLIENT_PORT)
    assert serveur.listen_fait is True
    assert serveur.client.timeout == 2
    assert len(serveur.client.envoye) == 1


def test_subscribe_msg():
    msg = subscribe_msg()

    assert msg["request"] == "subscribe"
    assert "port" in msg
    assert "name" in msg
    assert "matricules" in msg

