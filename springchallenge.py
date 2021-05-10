import sys
import math

def debug(*args, **kwargs):
    print(*args, **kwargs, file=sys.stderr, flush=True)

# class Ponderation:
#     def __init__(self):
#         self.unshadow_tree = 1

class Game:
    def __init__(self, nutrients, day):
        self.nutrients = nutrients
        self.day = day
        self.day_left = self._day_left()

    def _day_left(self):
        return 24 - self.day

class Cell:
    def __init__(self, richness, neighbours):
        self.richness = richness
        self.neighbours = [neigh for neigh in neighbours]
        self.own = False
        self.type = "empty"
        self.size_tree = -1

map = {}
game = Game(0,0)
number_of_cells = int(input())  # 37
for i in range(number_of_cells):
    # index: 0 is the center cell, the next cells spiral outwards
    # richness: 0 if the cell is unusable, 1-3 for usable cells
    # neigh_0: the index of the neighbouring cell for each direction
    index, richness, neigh_0, neigh_1, neigh_2, neigh_3, neigh_4, neigh_5 = [int(j) for j in input().split()]
    map[index] = Cell(richness, [neigh_0, neigh_1, neigh_2, neigh_3, neigh_4, neigh_5])


def shadows_generated_by_this_cell(index, day):
    i = 0
    shadows = []
    tmp = index
    while map[index].size_tree > i:
        tmp = map[tmp].neighbours[day % 6 * -1]
        shadows.append(tmp)
        i += 1
    return shadows

def being_shadowed_by(index, day):
    tmp = index
    shadowed = []
    for i in range(3):
        tmp = map[tmp].neighbours[(day % 6 + 3) % 6]
        if tmp == -1:
            break
        # debug("test:", tmp)
        if map[tmp].size_tree > i and map[tmp].size_tree >= map[index].size_tree:
            shadowed.append(tmp)
    return shadowed

def days_before_shadowed(index, day):
    for i in range(6):
        if len(being_shadowed_by(index, day + i)) > 0:
            return i
    return 7

def compute_cost_action(map, action):

    def cost_seed(map):
        cost = 0
        for key in dict(map):
            if map[key].size_tree == 0 and map[key].own:
                cost += 1
        return cost

    def cost_grow(map, index):
        if map[index].size_tree == 0:
            cost = 1
            for key in dict(map):
                if map[key].own and map[key].size_tree == 1:
                    cost += 1
        elif map[index].size_tree == 1:
            cost = 3
            for key in dict(map):
                if map[key].own and map[key].size_tree == 2:
                    cost += 1
        elif map[index].size_tree == 2:
            cost = 7
            for key in dict(map):
                if map[key].own and map[key].size_tree == 3:
                    cost += 1
        return cost

    if action.split(" ")[0] == "SEED":
        cost = cost_seed(map)
    elif action.split(" ")[0] == "GROW":
        cost = cost_grow(map, int(action.split(" ")[1]))
    elif action.split(" ")[0] == "COMPLETE":
        cost = 4
    elif action == "WAIT":
        cost = 0
    else:
        debug("L'action : ", action, " n'est pas geree")
        cost = 0
    return cost

def shadowed_days(cell):
    nb_day_shadowed = 0
    for day in range(game.day, game.day_left + game.day):
        if being_shadowed_by(cell, day):
            nb_day_shadowed += 1
    return nb_day_shadowed #jours d'ombres

list_possible_action = []

def compute_benefits_action(action):
    def shadowed_days_after_grow(cell):
        nb_day_shadowed_after = 0
        map[cell].size_tree += 1
        for day in range(game.day, game.day_left + game.day):
            if being_shadowed_by(cell, day):
                nb_day_shadowed_after += 1
        map[cell].size_tree -= 1
        return nb_day_shadowed_after

    def seed_benefits(action): # A OPTIMISER
        benefits = 0
        nb_seed = 0
        for i in range(len(map)):
            if map[i].size_tree == 0 and map[i].own:
                nb_seed += 1
        benefits = game.day_left - nb_seed ** 3 - game.nb_tree_own
        # return benefits + map[int(action.split(" ")[2])].richness
        return -3 + map[int(action.split(" ")[2])].richness


    def grow_benefits(action):
        cell = int(action.split(" ")[1])
        days_left = game.day_left
        day_shadowed = shadowed_days(cell)
        day_sun_win = shadowed_days(cell) - shadowed_days_after_grow(cell)
        
        #  + value = cache des arbres ennemis
        # - value = cache nos arbres
        
        return (game.day_left - (day_shadowed - day_sun_win)  / 3) + (map[int(cell)].richness * 2) - 2



    def calcul_point_richness(cell):
        if map[cell].richness == 1:
            return 0
        elif map[cell].richness == 2:
            return 2       
        elif map[cell].richness == 3:
            return 4    
        else:
            return 0

    benefits = 0
    if action.split(" ")[0] == "SEED":
        benefits = seed_benefits(action)
    elif action.split(" ")[0] == "GROW":
        benefits = grow_benefits(action)
    elif action.split(" ")[0] == "COMPLETE":
        benefits = game.nutrients + calcul_point_richness(int(action.split(" ")[1])) + game.day
    elif action == "WAIT":
        benefits = 0
    else:
        debug("L'action : ", action, " n'est pas geree")
        benefits = 0



    return benefits


def calcul_heuristique(action):
    heuristique = 0
    cell = action.split(" ")
    
    # heuristique += map[int(cell[1])].richness
    benefits = compute_benefits_action(action)
    cost = compute_cost_action(map, action)
    debug ("action :", action)
    debug("benefits de l'action :", benefits)
    debug("cost de l'action :", cost)
    heuristique +=  benefits - cost

    return (action, heuristique)

# game loop

while True:
    day = int(input())  # the game lasts 24 days: 0-23
    shadows = shadows_generated_by_this_cell(0, day)
    debug("Ombres generes par la case 0 : ", shadows)
    shadowed = being_shadowed_by(0, day)
    debug("Cells generant de l'ombre a la case ", 0, " : ", shadowed)
    days_before_sh = days_before_shadowed(0, day)
    debug("Nb days before shadowed : ", days_before_sh)
    nutrients = int(input())  # the base score you gain from the next COMPLETE action
    game.nutrients = nutrients
    game.day = day
    # sun: your sun points
    # score: your current score
    sun, score = [int(i) for i in input().split()]
    inputs = input().split()
    opp_sun = int(inputs[0])  # opponent's sun points
    opp_score = int(inputs[1])  # opponent's score
    opp_is_waiting = inputs[2] != "0"  # whether your opponent is asleep until the next day
    number_of_trees = int(input())  # the current amount of trees
    game.nb_tree_own = 0
    for i in range(number_of_trees):
        inputs = input().split()
        cell_index = int(inputs[0])  # location of this tree
        map[cell_index].size_tree = int(inputs[1])  # size of this tree: 0-3
        map[cell_index].own = True if inputs[2] != "0" else False
        game.nb_tree_own += 1 if map[cell_index].own else 0
        debug("NOMBRE DE TREE OWN", game.nb_tree_own)
        is_dormant = inputs[3] != "0"  # 1 if this tree is dormant NOT IN CELL
    number_of_possible_actions = int(input())  # all legal actions
    list_possible_action = []

    for i in range(number_of_possible_actions):
        possible_action = input()  # try printing something from here to start with
        list_possible_action.append((possible_action, 0))

    for idx, arg in enumerate(list_possible_action):
        list_possible_action[idx] = calcul_heuristique(arg[0])
    


    list_possible_action = sorted(list_possible_action, key=lambda x: x[1])
    debug("liste d'action avec heuristique pas boosté =" ,list_possible_action)
    print(list_possible_action[-1][0])
    
    # Write an action using print
    # To debug: print("Debug messages...", file=sys.stderr, flush=True)


    # GROW cellIdx | SEED sourceIdx targetIdx | COMPLETE cellIdx | WAIT <message>