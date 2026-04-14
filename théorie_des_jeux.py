#============== jeu tic tac toe ==========================
# The game state is a list of 9 items, grille = liste de 0-8 indices
# None is stored for empty cell
# 1 is stored for 'X' (player 1)
# 2 is stored for 'O' (player 2)

import random, time
from collections import defaultdict

lines = [
	[0, 1, 2], #même signes dans ligne 012
	[3, 4, 5],
	[6, 7, 8],
	[0, 3, 6], #même signes dans le colone 036
	[1, 4, 7],
	[2, 5, 8],
	[0, 4, 8], #diagonales
	[2, 4, 6]
]

def winner(state):
	for line in lines:
		values = set((state[i] for i in line)) #tous les elem dans l'ensemble (si plusieurs fois, in en garde qu'un)
		if len(values) == 1: #signifie que tout est le meme signe car 1 elem différent
			player = values.pop()
			if player is not None:
				return player
	return None

def utility(state, player): #prend état du jeu et joueur en cours (max la plus haute et min la plus basse possible)
	theWinner = winner(state)
	if theWinner is None: #pas de gagnart
		return 0
	if theWinner == player:
		return 1
	return -1 #c'est l'adversiare (toujours min pour adversaire du player en cours)

def gameOver(state):
	if winner(state) is not None:
		return True 

	empty = 0
	for elem in state:
		if elem is None:
			empty += 1
	return empty == 0 #cases vides = 0 jeu terminé

def currentPlayer(state): #calcul joueur actuel sur base des coups déjç joués
	counters = {1: 0, 2: 0, None: 0} #initialisé à zéro
	for elem in state:
		counters[elem] += 1
	
	if counters[1] == counters[2]:
		return 1 #joueur 1
	return 2

def moves(state): #donne tous les coups possible à jouer sur base d'un état
	res = []
	for i, elem in enumerate(state):
		if elem is None:
			res.append(i)
	
	random.shuffle(res) #renvoie les coups dans un ordre aléatoire (exploré ordre différent pour avoir partie différente)
	return res

def apply(state, move): # à partir d'un état et d'un mvmt : donne état suivant
	player = currentPlayer(state) # 1 ou 2 dans la case
	res = list(state) 
	res[move] = player
	return res

def MAX(state, player):
	if gameOver(state): #noeud terminal ?
		return utility(state, player), None #renvoyer none car noeud terminal

	theValue, theMove = float('-inf'), None #valeur de base (tout sera plus grand)
	for move in moves(state): #tous les mvmt faisables a partur de state
		successor = apply(state, move) #avoir le prochain (parcouru un a un)
		value, _ = MIN(successor, player) #prochain état en fonction de min (_ car on s'en fou du move qu'il a: variable blc)
		if value > theValue: #pour chaque valeur
			theValue, theMove = value, move #on garde la plus grande (meilleur) et le move associé
	return theValue, theMove

def MIN(state, player):
	if gameOver(state):
		return utility(state, player), None

	theValue, theMove = float('inf'), None #cherche un min
	for move in moves(state):
		successor = apply(state, move)
		value, _ = MAX(successor, player)
		if value < theValue: #min
			theValue, theMove = value, move
	return theValue, theMove



def negamax(state, player):
	if gameOver(state):
		return -utility(state, player), None

	theValue, theMove = float('-inf'), None
	for move in moves(state):
		successor = apply(state, move)
		value, _ = negamax(successor, player%2+1)
		if value > theValue:
			theValue, theMove = value, move
	return -theValue, theMove

def negamaxWithPruning(state, player, alpha=float('-inf'), beta=float('inf')):
	if gameOver(state):
		return -utility(state, player), None

	theValue, theMove = float('-inf'), None
	for move in moves(state):
		successor = apply(state, move)
		value, _ = negamaxWithPruning(successor, player%2+1, -beta, -alpha)
		if value > theValue:
			theValue, theMove = value, move
		alpha = max(alpha, theValue)
		if alpha >= beta: #pruning
			break
	return -theValue, theMove


#===== profondeur limitée : heuristique pour éviter parties infinies
def lineValue(line, player):
	counters = {
		1: 0,
		2: 0,
		None: 0
	}

	for elem in line:#compte le nombre de pion sur la ligne 
		counters[elem] += 1

	if counters[player] > counters[player%2+1]:
		return 1
	if counters[player] == counters[player%2+1]:
		return 0
	return -1


def heuristic(state, player):
	if gameOver(state):
		theWinner = winner(state)
		if theWinner is None:
			return 0
		if theWinner == player:
			return 9
		return -9
	res = 0
	for line in lines: #parcours les lignes et additionne le total (+ pour nous, - pour adversaire)
		res += lineValue([state[i] for i in line], player)
	return res
	
def negamaxWithPruningLimitedDepth(state, player, depth=4, alpha=float('-inf'), beta=float('inf')): #idem with pruning avec profondeur reçue
	if gameOver(state) or depth == 0: #s'arrête soit état final, soit
		return -heuristic(state, player), None

	theValue, theMove = float('-inf'), None
	for move in moves(state):
		successor = apply(state, move)
		value, _ = negamaxWithPruningLimitedDepth(successor, player%2+1, depth-1, -beta, -alpha)
		if value > theValue:
			theValue, theMove = value, move
		alpha = max(alpha, theValue)
		if alpha >= beta:
			break
	return -theValue, theMove 
#on ne pourra plus jouer parfaitement (estimation heuristique)
#======================================================
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#Profondeur itératif: attention il faudrait stopper si pas le temps de faire le prochaine profondeur 
def negamaxWithPruningIterativeDeepening(state, player, timeout=0.1):
	cache = defaultdict(lambda : 0)
	def cachedNegamaxWithPruningLimitedDepth(state, player, depth, alpha=float('-inf'), beta=float('inf')):
		over = gameOver(state)
		if over or depth == 0:
			res = -heuristic(state, player), None, over

		else:
			theValue, theMove, theOver = float('-inf'), None, True
			possibilities = [(move, apply(state, move)) for move in moves(state)]
			possibilities.sort(key=lambda poss: cache[tuple(poss[1])])
			for move, successor in reversed(possibilities):
				value, _, over = cachedNegamaxWithPruningLimitedDepth(successor, player%2+1, depth-1, -beta, -alpha)
				theOver = theOver and over
				if value > theValue:
					theValue, theMove = value, move
				alpha = max(alpha, theValue)
				if alpha >= beta:
					break
			res = -theValue, theMove, theOver
		cache[tuple(state)] = res[0]
		return res

	value, move = 0, None
	depth = 1
	start = time.time()
	over = False
	while value > -9 and time.time() - start < timeout and not over:
		value, move, over = cachedNegamaxWithPruningLimitedDepth(state, player, depth)
		depth += 1

	print('depth =', depth)
	return value, move
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def timeit(fun):
	def wrapper(*args, **kwargs):
		start = time.time()
		res = fun(*args, **kwargs)
		print('Executed in {}s'.format(time.time() - start))
		return res
	return wrapper

@timeit
def next(state, fun):
	player = currentPlayer(state)
	_, move = MAX(state, player)
	return move

def run(fun):
	state = [
		None, None, None,
		None, None, None,
		None, None, None,
	]
	show(state)
	while not gameOver(state):
		move = next(state, fun)
		state = apply(state, move)
		show(state)

def show(state): #affiche l'état demandé 
	state = ['X' if val == 1 else 
				'O' if val == 2 else 
				' ' for val in state]
	print(state[:3])
	print(state[3:6])
	print(state[6:])
	print()

state = [
	None, None, None,
	None, None, None,
	None, None, None,
]

run(negamaxWithPruningIterativeDeepening)  #plus rapide en appelant WithPruning