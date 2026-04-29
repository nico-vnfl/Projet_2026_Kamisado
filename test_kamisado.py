import pytest


from moves import (tile_color, piece, player_direction, generate_moves)
from IA import  (choix_move, compute_move)
from inscription import make_packet, subscribe_msg

def get_empty_board():
    
    return [[["red", None] for _ in range(8)] for _ in range(8)]



def test_tile_and_piece():
    cell = ["orange", ["blue", "dark"]]
    assert tile_color(cell) == "orange"
    assert piece(cell) == ["blue", "dark"]

    

def test_player_direction():
    assert player_direction(0) == -1
    assert player_direction(1) == 1

def test_generate_moves_simple_forward():
    
    board = get_empty_board()
    # pion du joueur 0
    board[6][3] = ["red", ["blue", "dark"]]

    moves = generate_moves(board, None, 0)
    assert [[6, 3], [5, 3]] in moves
    assert [[6, 3], [4, 3]] in moves

def test_generate_moves_bloque():
    
    board = get_empty_board()
    board[6][3] = ["red", ["blue", "dark"]]
    board[5][3] = ["red", ["yellow", "light"]]  # bloque l'avancement

    moves = generate_moves(board, None, 0)
    assert [[6, 3], [5, 3]] not in moves

def test_generate_moves_forced_color():
   
    board = get_empty_board()
    board[6][3] = ["red", ["blue", "dark"]]
    board[6][4] = ["red", ["yellow", "dark"]]

    moves = generate_moves(board, "blue", 0)
    for m in moves:
        assert m[0] == [6, 3]

def test_choose_move_prefers_forward():
    moves = [
        [[6, 3], [5, 3]],
        [[6, 3], [4, 3]],  
    ]
    best = choix_move(moves, 0)
    assert best == [[6, 3], [4, 3]]


def test_compute_move_créé():
    #
    board = get_empty_board()
    board[6][3] = ["red", ["blue", "dark"]]

    msg = {
        "state": {
            "board": board,
            "current": 0,
            "color": None
        }
    }
    move = compute_move(msg)
    assert move is not None



def test_make_packet():
    msg = {"response": "pong"}
    packet = make_packet(msg)
    assert isinstance(packet, bytes)
    assert len(packet) > 4  

def test_subscribe_msg():
    msg = subscribe_msg()
    assert msg["request"] == "subscribe"
    assert "port" in msg
    assert "name" in msg
    assert "matricules" in msg