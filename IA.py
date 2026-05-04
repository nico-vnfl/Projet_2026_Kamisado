from moves import generate_moves, piece, player_sides , tile_color

MAX_DEPTH = 16
TIME_LIMIT_SECONDS = 2.8
SCORE = 1_000_000

class SearchTimeout(Exception):
    pass

def compute_move(msg):
    return next_move(msg["state"])

def next_move(state):
    board = state["board"]
    player = int(state["current"])
    color = state.get("color")
    deadline = perf_counter() + TIME_LIMIT_SECONDS

    best_move = move_secours(board, player, color)
    try:
        for depth in range(1, MAX_DEPTH + 1):
            _, move = negamax(board, color, player, depth, float("-inf"), float("inf"), deadline)
            if move is not None:
                best_move = move
    except SearchTimeout:
        pass

    return best_move

def order_moves(board, legal_moves, player):
    direction = -1 if player == 0 else 1
    goal_row = 0 if player == 0 else 7

    def score(move):
        start, end = move
        win = 1 if end[0] == goal_row else 0
        advance = direction * (end[0] - start[0])
        straight = 1 if start[1] == end[1] else 0
        return (win, advance, straight)

    return sorted(legal_moves, key=score, reverse=True)

def clone_board(board):
    return [[cell[:] if piece(cell) is None else [cell[0], cell[1][:]] for cell in row] for row in board]



def get_winner(board):
    for col in range(8):
        top_piece = piece(board[0][col])
        if top_piece is not None and top_piece[1] == player_sides[0]:
            return 0

        bottom_piece = piece(board[7][col])
        if bottom_piece is not None and bottom_piece[1] == player_sides[1]:
            return 1

    return None


def choix_move(legal_moves, current):
    return order_moves(None, legal_moves, int(current))[0]


def move_secours(board, player, color=None):
    legal_moves = moves(board, color, player)
    if not legal_moves and color is not None:
        legal_moves = moves(board, None, player)
    if legal_moves:
        return order_moves(board, legal_moves, player)[0]
    return [[0, 0], [0, 0]]