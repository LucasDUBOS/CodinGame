import sys
import math

def debug(*args, **kwargs):
    print(*args, **kwargs, file=sys.stderr, flush=True)

class Game:
    def __init__(self, number_of_cells = 37, nutrients = 20, day = 0, sun = 0, score = 0, opp_sun = 0, opp_score = 0, opp_is_waiting = False, number_of_trees = 4, nb_tree_own = 2):
        self.number_of_cells = number_of_cells
        self.nutrients = nutrients
        self.day = day
        self.day_left = self._day_left()
        self.sun = sun
        self.score = score
        self.opp_sun = opp_sun
        self.opp_score = opp_score
        self.opp_is_waiting = opp_is_waiting != 0
        self.number_of_trees = number_of_trees
        self.nb_tree_own = nb_tree_own

    def _day_left(self):
        return 24 - self.day

class Cell:
    def __init__(self, richness, neighbours, is_dormant = False):
        self.richness = richness
        self.neighbours = neighbours
        self.own = False
        self.type = "empty"
        self.size_tree = -1
        self.is_dormant = is_dormant
        self.shadow_potential = {}


def reset_infos():
    game.nb_tree_own = 0
    for cell in map:
        map[cell].shadowed_by_us = 0
        map[cell].shadowed_by_him = 0
        map[cell].potential_shadowed_by_us = 0
        map[cell].potential_shadowed_by_him = 0

def shadows_generated_by_this_cell(index, day, size_tree):
    i = 0
    shadows = []
    tmp = index
    while size_tree > i:
        tmp = map[tmp].neighbours[day % 6]
        if tmp == -1:
            break
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

def shadow_projected(tree):
    for day in range(6):
        for i in range(len(tree.shadow_potential[day])):
            if i <= tree.size_tree:
                if tree.own:
                    map[tree.shadow_potential[day][i]].shadowed_by_us += 1
                else:
                    map[tree.shadow_potential[day][i]].shadowed_by_him += 1
            if tree.own:
                map[tree.shadow_potential[day][i]].potential_shadowed_by_us += 1
            else:
                map[tree.shadow_potential[day][i]].potential_shadowed_by_him += 1

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

def calcul_heuristique(action):
    return 0

def reception_info():
    # general game infos
    game.day = int(input())  # the game lasts 24 days: 0-23
    game.nutrients = int(input())  # the base score you gain from the next COMPLETE action

    # nos game infos
    game.sun, game.score = [int(i) for i in input().split()]

    # adversaire game infos
    game.opp_sun, game.opp_score, game.opp_is_waiting = [int(i) for i in input().split()]

    # infos trees
    game.number_of_trees = int(input())  # the current amount of trees
    reset_infos()
    for i in range(game.number_of_trees):
        inputs = input().split()
        cell_index = int(inputs[0])  # location of this tree
        tree = map[cell_index]
        tree.size_tree = int(inputs[1])  # size of this tree: 0-3
        tree.own = True if inputs[2] != "0" else False
        game.nb_tree_own += 1 if tree.own else 0
        tree.is_dormant = inputs[3] != "0"  # 1 if this tree is dormant NOT IN CELL
        shadow_projected(tree)

if __name__ == "__main__":
    game = Game()
    game.number_of_cells = int(input())

    # map info
    map = {}
    for i in range(game.number_of_cells):
        index, richness, neigh_0, neigh_1, neigh_2, neigh_3, neigh_4, neigh_5 = [int(j) for j in input().split()]
        map[index] = Cell(richness, (neigh_0, neigh_1, neigh_2, neigh_3, neigh_4, neigh_5))

    for cell in range(game.number_of_cells):
        for day in range(6):
            # map[cell][day] = shadows_generated_by_this_cell(cell, day, 3)
            map[cell].shadow_potential[day] = shadows_generated_by_this_cell(cell, day, 3)
    
    debug("ombre generes par map[0].shadow_potential : ", map[0].shadow_potential)

    while True:
        
        reception_info()
        
        # 
        number_of_actions = int(input())  # all legal actions
        list_actions = []
        for i in range(number_of_actions):
            action = input()  # try printing something from here to start with
            heuristique = calcul_heuristique(action)
            list_actions.append((action, heuristique))


        list_actions = sorted(list_actions, key=lambda x: x[1])
        for action in list_actions:
            debug("Action : ", action[0], " -- Heuristique : ", action[1], "\n")
        print(list_actions[-1][0], list_actions[-1][0])
    


    # Write an action using print
    # To debug: print("Debug messages...", file=sys.stderr, flush=True)


    # GROW cellIdx | SEED sourceIdx targetIdx | COMPLETE cellIdx | WAIT <message>