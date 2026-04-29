player_sides = {
    0: "dark",
    1: "light",
}

def tile_color(cell):
    return cell[0]

def piece(cell):
    return cell[1]


def player_direction(current_player):
    if current_player == 0:
        return -1
    return 1
def generate_moves(board, forced_color, current_player):
    current_player = int(current_player)
    moves = []
    direction = player_direction(current_player)
    directions = [ (direction, 0), (direction, -1), (direction, 1) ]

    for row in range(8):
        for col in range(8):
            cell = board[row][col]
            if piece(cell) is None:
                continue
            if piece(cell)[1] != player_sides[current_player]:
                continue
            if forced_color is not None:
                if piece(cell)[0] != forced_color:
                    continue
           

            for diff_row, diff_col in directions:
                next_row = row + diff_row
                next_col = col + diff_col

                while 0 <= next_row < 8 and 0 <= next_col < 8:
                    if piece(board[next_row][next_col]) is not None:
                        break

                    moves.append([[row, col], [next_row, next_col]])
                    next_row += diff_row
                    next_col += diff_col

    return moves
