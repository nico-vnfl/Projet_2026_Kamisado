from moves import generate_moves, piece, player_sides , tile_color


def compute_move(msg):
    return next_move(msg["state"])


def choix_move(legal_moves, current):
    return order_moves(None, legal_moves, int(current))[0]


def move_secours(board, player, color=None):
    legal_moves = moves(board, color, player)
    if not legal_moves and color is not None:
        legal_moves = moves(board, None, player)
    if legal_moves:
        return order_moves(board, legal_moves, player)[0]
    return [[0, 0], [0, 0]]