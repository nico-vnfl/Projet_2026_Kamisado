from time import perf_counter
from moves import generate_moves, piece, player_sides , tile_color

MAX_DEPTH = 16
TIME_LIMIT_SECONDS = 2.8
SCORE = 1_000_000

class SearchTimeout(Exception):
    pass

def compute_move(msg):
    state = msg["state"]
    move = next_move(state)
    return ensure_legal_move(state, move)

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

def negamax(board, color, player, depth, alpha, beta, deadline):
    check_deadline(deadline)

    if gameOver(board):
        return utility(board, player), None

    legal_moves = moves(board, color, player)
    if depth == 0 or not legal_moves:
        return evaluation(board, player), None

    best_value = float("-inf")
    best_move = None

    for move in order_moves(board, legal_moves, player):
        new_board, new_color = apply(board, move)
        value, _ = negamax(new_board, new_color, 1 - player, depth - 1, -beta, -alpha, deadline)
        value = -value

        if value > best_value:
            best_value = value
            best_move = move

        alpha = max(alpha, best_value)
        if alpha >= beta:
            break

    return best_value, best_move


def check_deadline(deadline):
    if perf_counter() >= deadline:
        raise SearchTimeout


def moves(board, color, player):
    return generate_moves(board, color, player)


def apply(board, move):
    start, end = move
    new_board = clone_board(board)

    moving_piece = new_board[start[0]][start[1]][1]
    new_board[start[0]][start[1]][1] = None
    new_board[end[0]][end[1]][1] = moving_piece

    return new_board, tile_color(new_board[end[0]][end[1]])


def gameOver(board):
    return get_winner(board) is not None


def utility(board, player):
    winner = get_winner(board)

    if winner is None:
        return 0
    if winner == player:
        return SCORE
    return -SCORE


def evaluation(board, player):
    opponent = 1 - player
    return score_player(board, player) - score_player(board, opponent)


def score_player(board, player):
    side = player_sides[player]
    direction = -1 if player == 0 else 1
    score = 0

    for row in range(8):
        for col in range(8):
            p = piece(board[row][col])
            if p is None or p[1] != side:
                continue

            progress = 7 - row if player == 0 else row
            center = 4 - abs(3.5 - col)
            score += progress * 100
            score += center * 10

            next_row = row + direction
            if 0 <= next_row < 8 and piece(board[next_row][col]) is None:
                score += 15

    return score


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
    if legal_moves:
        return order_moves(board, legal_moves, player)[0]
    return [[0, 0], [0, 0]]

def ensure_legal_move(state, move):
    board = state["board"]
    player = int(state["current"])
    color = state.get("color")
    legal_moves = moves(board, color, player)

    if move in legal_moves:
        return move
    if legal_moves:
        return order_moves(board, legal_moves, player)[0]
    return [[0, 0], [0, 0]]