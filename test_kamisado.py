import pytest
import json
import struct
from time import perf_counter
from unittest.mock import MagicMock

from moves import tile_color, piece, player_direction, generate_moves
from IA import (
    choix_move, compute_move, get_pass_move, apply, gameOver,
    get_winner, utility, evaluation, score_player, order_moves,
    clone_board, move_secours, ensure_legal_move, check_deadline,
    SearchTimeout, SCORE
)
from inscription import make_packet, subscribe_msg, recvall, receive_message, send_move


def get_empty_board():
    return [[["red", None] for _ in range(8)] for _ in range(8)]

def test_tile_color():
    cell = ["orange", ["blue", "dark"]]
    assert tile_color(cell) == "orange"

def test_piece():
    cell = ["orange", ["blue", "dark"]]
    assert piece(cell) == ["blue", "dark"]

def test_piece_vide():
    assert piece(["red", None]) is None

def test_player_direction():
    assert player_direction(0) == -1
    assert player_direction(1) == 1

def test_generate_moves_avance():
    board = get_empty_board()
    board[6][3] = ["red", ["blue", "dark"]]
    mvs = generate_moves(board, None, 0)
    assert [[6, 3], [5, 3]] in mvs
    assert [[6, 3], [4, 3]] in mvs
    assert all(m[0] == [6, 3] for m in mvs)

def test_generate_moves_bloque():
    board = get_empty_board()
    board[6][3] = ["red", ["blue", "dark"]]
    board[5][3] = ["red", ["yellow", "light"]]
    mvs = generate_moves(board, None, 0)
    assert [[6, 3], [5, 3]] not in mvs

def test_generate_moves_couleur_forcee():
    board = get_empty_board()
    board[6][3] = ["red", ["blue", "dark"]]
    board[6][4] = ["red", ["yellow", "dark"]]
    mvs = generate_moves(board, "blue", 0)
    for m in mvs:
        assert m[0] == [6, 3]

def test_generate_moves_joueur1():
    board = get_empty_board()
    board[1][3] = ["red", ["blue", "light"]]
    mvs = generate_moves(board, None, 1)
    assert [[1, 3], [2, 3]] in mvs
    assert [[1, 3], [3, 3]] in mvs


def test_clone_board_independant():
    board = get_empty_board()
    board[3][3] = ["red", ["blue", "dark"]]
    clone = clone_board(board)
    clone[3][3][1] = None
    assert piece(board[3][3]) == ["blue", "dark"]

def test_apply_coup_normal():
    board = get_empty_board()
    board[6][3] = ["blue", ["blue", "dark"]]
    new_board, new_color = apply(board, [[6, 3], [5, 3]])
    assert piece(new_board[5][3]) == ["blue", "dark"]
    assert piece(new_board[6][3]) is None
    assert new_color == "red"

def test_apply_pass():
    board = get_empty_board()
    board[1][3] = ["brown", ["brown", "dark"]]
    new_board, new_color = apply(board, [[1, 3], [1, 3]])
    assert piece(new_board[1][3]) == ["brown", "dark"]
    assert new_color == "brown"

def test_get_winner_aucun():
    board = get_empty_board()
    assert get_winner(board) is None

def test_get_winner_joueur0():
    board = get_empty_board()
    board[0][4] = ["red", ["blue", "dark"]]
    assert get_winner(board) == 0

def test_get_winner_joueur1():
    board = get_empty_board()
    board[7][4] = ["red", ["blue", "light"]]
    assert get_winner(board) == 1

def test_gameover_false():
    board = get_empty_board()
    board[3][3] = ["red", ["blue", "dark"]]
    assert gameOver(board) == False

def test_gameover_true():
    board = get_empty_board()
    board[0][3] = ["red", ["blue", "dark"]]
    assert gameOver(board) == True

def test_utility_victoire():
    board = get_empty_board()
    board[0][3] = ["red", ["blue", "dark"]]
    assert utility(board, 0) == SCORE
    assert utility(board, 1) == -SCORE

def test_utility_pas_de_gagnant():
    board = get_empty_board()
    assert utility(board, 0) == 0

def test_get_pass_move_trouve():
    board = get_empty_board()
    board[1][3] = ["brown", ["brown", "dark"]]
    assert get_pass_move(board, "brown", 0) == [[1, 3], [1, 3]]

def test_get_pass_move_fallback():
    board = get_empty_board()
    assert get_pass_move(board, "brown", 0) == [[0, 0], [0, 0]]


def test_evaluation_symetrie():
    board = get_empty_board()
    board[3][3] = ["red", ["blue", "dark"]]
    board[4][4] = ["red", ["blue", "light"]]
    assert evaluation(board, 0) == -evaluation(board, 1)

def test_score_player_progression():
    board = get_empty_board()
    board[1][3] = ["red", ["blue", "dark"]]   
    board[6][3] = ["red", ["yellow", "dark"]]  
    assert score_player(board, 0) > 0

def test_score_player_chemin_degage():
    board = get_empty_board()
    board[3][3] = ["red", ["blue", "dark"]]    
    assert score_player(board, 0) > 0

def test_score_player_joueur1():
    board = get_empty_board()
    board[5][3] = ["red", ["blue", "light"]]
    assert score_player(board, 1) > 0



def test_order_moves_victoire_en_premier():
    mvs = [
        [[3, 3], [2, 3]],
        [[1, 3], [0, 3]], 
    ]
    assert order_moves(mvs, 0)[0] == [[1, 3], [0, 3]]

def test_order_moves_avance_avant_recul():
    mvs = [
        [[6, 3], [7, 3]],  
        [[6, 3], [5, 3]], 
    ]
    assert order_moves(mvs, 0)[0] == [[6, 3], [5, 3]]

def test_order_moves_joueur1():
    mvs = [
        [[1, 3], [0, 3]],  
        [[1, 3], [2, 3]],  
    ]
    assert order_moves(mvs, 1)[0] == [[1, 3], [2, 3]]

def test_move_secours_normal():
    board = get_empty_board()
    board[6][3] = ["red", ["blue", "dark"]]
    m = move_secours(board, 0)
    assert m is not None
    assert m[0] == [6, 3]

def test_move_secours_pass():
    board = get_empty_board()
    board[1][3] = ["brown", ["brown", "dark"]]
    board[0][2] = ["red", ["x", "light"]]
    board[0][3] = ["red", ["x", "light"]]
    board[0][4] = ["red", ["x", "light"]]
    assert move_secours(board, 0, color="brown") == [[1, 3], [1, 3]]

def test_move_secours_aucune_piece():
    board = get_empty_board()
    assert move_secours(board, 0) == [[0, 0], [0, 0]]

def test_ensure_legal_move_legal():
    board = get_empty_board()
    board[6][3] = ["red", ["blue", "dark"]]
    state = {"board": board, "current": 0, "color": None}
    assert ensure_legal_move(state, [[6, 3], [5, 3]]) == [[6, 3], [5, 3]]

def test_ensure_legal_move_illegal():
    board = get_empty_board()
    board[6][3] = ["red", ["blue", "dark"]]
    state = {"board": board, "current": 0, "color": None}
    result = ensure_legal_move(state, [[9, 9], [9, 9]])
    assert result in generate_moves(board, None, 0)

def test_ensure_legal_move_pass():
    board = get_empty_board()
    board[1][3] = ["brown", ["brown", "dark"]]
    board[0][2] = ["red", ["x", "light"]]
    board[0][3] = ["red", ["x", "light"]]
    board[0][4] = ["red", ["x", "light"]]
    state = {"board": board, "current": 0, "color": "brown"}
    assert ensure_legal_move(state, [[9, 9], [9, 9]]) == [[1, 3], [1, 3]]

def test_ensure_legal_move_aucune_piece():
    board = get_empty_board()
    state = {"board": board, "current": 0, "color": None}
    assert ensure_legal_move(state, [[9, 9], [9, 9]]) == [[0, 0], [0, 0]]

def test_check_deadline_timeout():
    with pytest.raises(SearchTimeout):
        check_deadline(perf_counter() - 1)


def test_compute_move_basique():
    board = get_empty_board()
    board[6][3] = ["red", ["blue", "dark"]]
    msg = {"state": {"board": board, "current": 0, "color": None}}
    move = compute_move(msg)
    assert move is not None

def test_compute_move_victoire_immediate():
    board = get_empty_board()
    board[2][3] = ["red", ["blue", "dark"]]
    board[6][4] = ["red", ["yellow", "dark"]]
    msg = {"state": {"board": board, "current": 0, "color": "blue"}}
    assert compute_move(msg) == [[2, 3], [0, 3]]

def test_compute_move_couleur_forcee_bloquee():
    board = get_empty_board()
    board[1][6] = ["brown", ["green", "dark"]]
    board[0][5] = ["red", ["yellow", "light"]]
    board[0][6] = ["green", ["green", "light"]]
    board[0][7] = ["brown", ["purple", "light"]]
    msg = {"state": {"board": board, "current": 0, "color": "green"}}
    move = compute_move(msg)
    assert move == [[1, 6], [1, 6]]

def test_compute_move_pass_obligatoire():
    board = get_empty_board()
    board[1][3] = ["brown", ["brown", "dark"]]
    board[0][2] = ["red", ["x", "light"]]
    board[0][3] = ["red", ["x", "light"]]
    board[0][4] = ["red", ["x", "light"]]
    msg = {"state": {"board": board, "current": 0, "color": "brown"}}
    assert compute_move(msg) == [[1, 3], [1, 3]]

def test_choix_move_prefere_avance():
    mvs = [
        [[6, 3], [5, 3]],
        [[6, 3], [4, 3]],
    ]
    assert choix_move(mvs, 0) == [[6, 3], [4, 3]]

def test_make_packet():
    packet = make_packet({"response": "pong"})
    assert isinstance(packet, bytes)
    assert len(packet) > 4

def test_make_packet_length_in_bits():
    packet = make_packet({"response": "pong"}, length_in_bits=True)
    assert isinstance(packet, bytes)

def test_subscribe_msg():
    msg = subscribe_msg()
    assert msg["request"] == "subscribe"
    assert "port" in msg
    assert "name" in msg
    assert "matricules" in msg

def test_recvall_complet():
    sock = MagicMock()
    sock.recv.return_value = b"hello"
    assert recvall(sock, 5) == b"hello"

def test_recvall_deconnexion():
    sock = MagicMock()
    sock.recv.return_value = b""
    assert recvall(sock, 5) is None

def test_receive_message_ok():
    data = json.dumps({"request": "ping"}).encode()
    header = struct.pack("I", len(data))
    sock = MagicMock()
    sock.recv.side_effect = [header, data]
    assert receive_message(sock) == {"request": "ping"}

def test_receive_message_vide():
    sock = MagicMock()
    sock.recv.return_value = b""
    assert receive_message(sock) is None

def test_send_move():
    sock = MagicMock()
    send_move(sock, [[1, 2], [3, 4]])
    sock.sendall.assert_called_once()
