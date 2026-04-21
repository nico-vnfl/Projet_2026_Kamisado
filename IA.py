def compute_move(msg): #IA qui va tout droit 
    state = msg["state"]
    board = state["board"]
    color = state["color"]

    from_l = from_c = None #initialisation

    for l in range(8):
        for c in range(8):
            case = board[l][c]
            if case and case[0] == "Nico" and (color is None or case[1] == color):
                from_l, from_c = l, c
    if from_l is None:
        print("ERREUR: pion introuvable")
        return [[0,0], [0,0]] #vérif pion là ?
    
    if state["current"] == 0:
        to_l = from_l - 1
        to_c = from_c
    if state["current"] == 1:
        to_l = from_l + 1 
        to_c = from_c

    if 0 <= to_l < 8 and board[to_l][to_c] is None:
        return [[from_l, from_c], [to_l, to_c]] #case libre ?
    
    return [[from_l, from_c], [from_l, from_c]]


# ajouter plus tard : 
#moves = generate_moves(board, color, player_name)
#best = best_move(moves)
#return best