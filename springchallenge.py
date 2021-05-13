import sys
import math


def debug(*args, **kwargs):
    print(*args, **kwargs, file=sys.stderr, flush=True)

class Game:
    def __init__(self, number_of_cells = 37, nutrients = 20, day = 0, sun = 0, score = 0, opp_sun = 0, opp_score = 0, opp_is_waiting = False, number_of_trees = 4, nb_tree_own = 2):
        self.number_of_cells = number_of_cells
        self.nutrients = nutrients
        self.day = day
        self.day_left = 24 - self.day
        self.sun = sun
        self.score = score
        self.opp_sun = opp_sun
        self.opp_score = opp_score
        self.opp_is_waiting = opp_is_waiting != 0
        self.number_of_trees = number_of_trees
        self.nb_tree_own = nb_tree_own


class Cell:
    def __init__(self, richness, neighbours, is_dormant = False):
        self.richness = richness
        self.neighbours = neighbours
        self.own = False
        self.type = "empty"
        self.size_tree = -1
        self.is_dormant = is_dormant
        self.shadow_potential = {}
        
def calcul_nb_arbre():
    list_tree = [0, 0, 0]
    for i in map:
        if map[i].size_tree == 1 and map[i].own:
            list_tree[0] += 1
        elif map[i].size_tree == 2 and map[i].own:
            list_tree[1] += 1
        elif map[i].size_tree == 3 and map[i].own:
            list_tree[2] += 1
    return list_tree

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
            cost = 0
            for key in dict(map):
                if map[key].own and map[key].size_tree == 1:
                    cost += 1
        elif map[index].size_tree == 1:
            cost = 0
            for key in dict(map):
                if map[key].own and map[key].size_tree == 2:
                    cost += 1
        elif map[index].size_tree == 2:
            cost = 0
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

def calcul_point_richness(cell):
    if map[cell].richness == 1:
        return 0
    elif map[cell].richness == 2:
        return 2       
    elif map[cell].richness == 3:
        return 4    
    else:
        return 0



def seed_heuristique(action):
    # dans liste seed:
    # -/ ombrage generé sur nos arbres 
    # -/ ombrages generé sur arbres ennemi 
    # - if map free (ratio) == pas planter sur case generant de l'ombre pour nous (ratio = cell / nb_tree )
    # -/ richness (pondéré)
    # - ne plus planter quand on ne peut pas faire pousser tout les arbres
    nb_tree = calcul_nb_arbre()
    flag0 = False
    flag1 = False
    flag2 = False
    if nb_tree[0] >= 1:
        for cell in map:
            if map[cell].size_tree == 1 and map[cell].own and not map[cell].is_dormant:
                flag1 = True
            elif map[cell].size_tree == 0 and map[cell].own and not map[cell].is_dormant:
                flag0 = True
            if map[cell].size_tree == 0:
                flag2 = True
        if (flag1 or flag0) and flag2:
            return -1

    potentiel = game.day_left * 3 - (1 + nb_tree[0]) - (3 + nb_tree[1]) - (7 + nb_tree[2]) - (3 * 3) - (3 * 2) - (3)
    cell = int(action.split()[2])
    heuristique = 0
    heuristique -= map[cell].potential_shadowed_by_us * 10
    heuristique += map[cell].potential_shadowed_by_him * 2
    heuristique += calcul_point_richness(cell) * 3 # GAME NUTRIENTS
    if map[int(action.split()[1])].size_tree == 1 or (game.day_left < 4 and flag2):
        return -1
    return heuristique + potentiel


def cost_grow_tmp(map, index):
    # dans liste GROW:
    # -/ cout
    # -/ ombrage généré supplémentaire ()
    # -/ passage soleil si on grow ? 
    # -/ generation soleil (calcul heuristique)
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

def grow_heuristique(action):
    nb_tree = calcul_nb_arbre()
    cell = int(action.split()[1])
    heuristique = 0

    size_tree = map[cell].size_tree
    if size_tree == 0:
        growth_cost = (1 + nb_tree[0]) + (3 + nb_tree[1]) + (7 + nb_tree[2]) + (3 * 3) + (3 * 2) + (3)
    elif size_tree == 1:
        growth_cost = (3 + nb_tree[1]) + (7 + nb_tree[2]) + (3 * 2) + (3)
    elif size_tree == 2:
        growth_cost = (7 + nb_tree[2]) + 3
    
    potentiel = game.day_left * 3 - growth_cost

    own_block = 0
    ennemy_block = 0
    for day in range(6): # ombrage généré supplémentaire
        for i in range(len(map[cell].shadow_potential[day])):
            if (map[map[cell].shadow_potential[day][i]].size_tree == map[cell].size_tree or map[map[cell].shadow_potential[day][i]].size_tree == map[cell].size_tree + 1) and i <= map[cell].size_tree:
                if map[map[cell].shadow_potential[day][i]].own:
                    own_block += map[map[cell].shadow_potential[day][i]].size_tree
                else:
                    ennemy_block += map[map[cell].shadow_potential[day][i]].size_tree
    heuristique = potentiel - (own_block * game.day_left / 6) + (ennemy_block * game.day_left / 6)
    tmp = days_before_shadowed(cell, game.day)
    map[cell].size_tree += 1
    heuristique += map[cell].size_tree if (days_before_shadowed(cell, game.day) - tmp) > 0 and tmp == 1 else 0 #soleil gagné en le montant maintenant
    map[cell].size_tree -= 1
    # heuristique -= compute_cost_action(map, action)
    heuristique += calcul_point_richness(cell) * 3 # pour départager en cas d'égalité

    # rajouté nutrients
    # if cost_grow_tmp(map, cell) > game.day_left and calcul_nb_arbre()[2] >= 1:
    #     heuristique = 0
    return heuristique

def complete_heuristique(cell):
    # a completer
    # - ombre qui est généré sur cette arbre
    # - prevoir fin de day pour couper tout les arbres de taille 3 (calcul heuristique)
    # - if nutriments high and ombrage léger and cost new size 3 high 
    nb_tree = calcul_nb_arbre()

    # heuristique = 4 * 3 + 4 * game.nutrients - (3 * game.day_left * (1 / nb_tree[2])) # 4 * 3 ?
    heuristique = game.nutrients * 3 - (3 * game.day_left) # point de soleil gagné = nutrients * 3) - (point de soleil non généré)
    debug("COMPLETE ", cell, "\n", "heuristique =", heuristique, "game.nutrients = ", game.nutrients, "game.day_left = ", game.day_left, "game.day =", game.day)
    # on deduit le l'ombre qui nous genere
    # on ajoute l'ombre qu'il genere sur l'ennemie
    own_block = 0
    ennemy_block = 0
    for day in range(6): # ombrage généré supplémentaire
        for i in range(len(map[cell].shadow_potential[day])):
            if map[map[cell].shadow_potential[day][i]].size_tree == map[cell].size_tree:
                if map[map[cell].shadow_potential[day][i]].own:
                    own_block += map[map[cell].shadow_potential[day][i]].size_tree
                else:
                    ennemy_block += map[map[cell].shadow_potential[day][i]].size_tree
    heuristique += own_block * game.day_left / 6 # nb de point de soleil qu'on se deny par taille arbre * (temps de deny / 6)
    heuristique -= ennemy_block * game.day_left / 6 # nb de point de soleil qu'on deny par taille arbre * (temps de deny / 6)
    debug("apres les deny d'ombres", "heuristique =", heuristique)
    heuristique += map[cell].size_tree if days_before_shadowed(cell, game.day) == 1 else 0 #soleil gagné en le montant maintenant
    heuristique += nb_tree[2] # soleil perdu pour refaire pousser un arbre
    heuristique += calcul_point_richness(cell) * 4
    return heuristique

#  dans la liste des 3 meilleurs action (seed, grow, complete) :
# - if no size_tree == 0 : SEED and day_left = enough to pousser l'arbre
# - Forcer full complete sur la fin and forcer complete a max tree (size 3) en fonction calcul premier tour

def calcul_heuristique(action):
    list_action = action.split()
    heuristique = 0
    if list_action[0] == "SEED":
        heuristique = seed_heuristique(action) / (compute_cost_action(map, action) + 1)
    elif list_action[0] == "GROW":
        heuristique = grow_heuristique(action) / (compute_cost_action(map, action) + 1)
    elif list_action[0] == "COMPLETE":
        heuristique = complete_heuristique(int(list_action[1])) / (compute_cost_action(map, action) + 1)
    # elif list_action[0] == "WAIT":
    #     if game.day < 2:
    #         heuristique = 0

    return heuristique

def reception_info():
    # general game infos
    reset_infos()
    game.day = int(input())  # the game lasts 24 days: 0-23
    game.nutrients = int(input())  # the base score you gain from the next COMPLETE action
    game.day_left = 24 - game.day


    # nos game infos
    game.sun, game.score = [int(i) for i in input().split()]

    # adversaire game infos
    game.opp_sun, game.opp_score, game.opp_is_waiting = [int(i) for i in input().split()]

    # infos trees
    game.number_of_trees = int(input())  # the current amount of trees
    
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
    
    # debug("ombre generes par map[0].shadow_potential : ", map[0].shadow_potential)

    while True:
        reception_info()
        debug("Bonjour, nous somme jour", game.day, "il reste donc", game.day_left, "jours")
        debug("Il reste actuellement", game.nutrients, "nutriments")
        number_of_actions = int(input())  # all legal actions
        list_actions = []
        for i in range(number_of_actions):
            action = input()  # try printing something from here to start with
            heuristique = calcul_heuristique(action)
            list_actions.append((action, heuristique))


        list_actions = sorted(list_actions, key=lambda x: x[1])
        # for action in list_actions:
        #     debug("Action : ", action[0], " -- Heuristique : ", action[1], "\n")
        if len(list_actions) > 5:
            for i in range(int(len(list_actions) / 2), len(list_actions)):
                debug("Action : ", list_actions[i][0], " -- Heuristique : ", list_actions[i][1], "\n")
        print(list_actions[-1][0], list_actions[-1][0])
    


    # Write an action using print
    # To debug: print("Debug messages...", file=sys.stderr, flush=True)


    # GROW cellIdx | SEED sourceIdx targetIdx | COMPLETE cellIdx | WAIT <message>