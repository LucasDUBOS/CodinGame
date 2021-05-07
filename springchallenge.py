import sys
import math

def debug(*args, **kwargs):
    print(*args, **kwargs, file=sys.stderr, flush=True)

# Auto-generated code below aims at helping you parse
# the standard input according to the problem statement.

map = {}

class Cell:
    def __init__(self, richness, neighbours):
        self.richness= richness
        self.neighbours = [neigh for neigh in neighbours]
        self.own = False
        self.type = "empty"
        self.size_tree = 0

number_of_cells = int(input())  # 37
for i in range(number_of_cells):
    # index: 0 is the center cell, the next cells spiral outwards
    # richness: 0 if the cell is unusable, 1-3 for usable cells
    # neigh_0: the index of the neighbouring cell for each direction
    index, richness, neigh_0, neigh_1, neigh_2, neigh_3, neigh_4, neigh_5 = [int(j) for j in input().split()]
    map[index] = Cell(richness, [neigh_0, neigh_1, neigh_2, neigh_3, neigh_4, neigh_5])


list_possible_action = []

def calcul_heuristique(action):
    heuristique = 0
    cell = action.split(" ")
    if len(cell) == 2:
        heuristique += map[int(cell[1])].richness

    return (action, heuristique)

# game loop
while True:
    day = int(input())  # the game lasts 24 days: 0-23
    nutrients = int(input())  # the base score you gain from the next COMPLETE action
    # sun: your sun points
    # score: your current score
    sun, score = [int(i) for i in input().split()]
    inputs = input().split()
    opp_sun = int(inputs[0])  # opponent's sun points
    opp_score = int(inputs[1])  # opponent's score
    opp_is_waiting = inputs[2] != "0"  # whether your opponent is asleep until the next day
    number_of_trees = int(input())  # the current amount of trees
    for i in range(number_of_trees):
        inputs = input().split()
        cell_index = int(inputs[0])  # location of this tree
        map[cell_index].size_tree = int(inputs[1])  # size of this tree: 0-3
        map[cell_index].own = True if inputs[2] != "0" else False
        is_dormant = inputs[3] != "0"  # 1 if this tree is dormant NOT IN CELL
    number_of_possible_actions = int(input())  # all legal actions
    list_possible_action = []

    for i in range(number_of_possible_actions):
        possible_action = input()  # try printing something from here to start with
        list_possible_action.append((possible_action, 0))

    for idx, arg in enumerate(list_possible_action):
        list_possible_action[idx] = calcul_heuristique(arg[0])
    
    list_possible_action = sorted(list_possible_action, key=lambda x: x[1])
    print(list_possible_action[-1][0])
    
    # Write an action using print
    # To debug: print("Debug messages...", file=sys.stderr, flush=True)


    # GROW cellIdx | SEED sourceIdx targetIdx | COMPLETE cellIdx | WAIT <message>

