from moves import generate_moves, piece, player_sides


def compute_move(msg):
    state = msg["state"]
    board = state["board"]
    color = state.get("color")
    current = state.get("current")

    moves = generate_moves(board, color, current)

    if not moves:
        print("ERREUR: aucun coup autorisé trouvé t'es nulll")
        print("current =", current, "couleur =", color)
        return move_secours(board, current)

    return choix_move(moves, current)


def choix_move(moves, current):
    direction = -1 if current == 0 else 1

    def score(move):
        start, end = move
        distance = abs(end[0] - start[0])
        avancer = direction * (end[0] - start[0])
        bonus_ligne = 1 if start[1] == end[1] else 0
        return (avancer, distance, bonus_ligne)

    return max(moves, key=score)


def move_secours(board, current):
    direction = -1 if int(current) == 0 else 1

    for row in range(8):
        for col in range(8):
            cell = board[row][col]

            if piece(cell) is None:
                continue

            if piece(cell)[1] != player_sides[int(current)]:
                continue

            next_row = row + direction
            if 0 <= next_row < 8 and piece(board[next_row][col]) is None:
                move = [[row, col], [next_row, col]]
                print("COUP DE SECOURS =", move)
                return move

    print("COUP DE SECOURS = [[0, 0], [0, 0]]")
    return [[0, 0], [0, 0]]