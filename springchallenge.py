import sys
import math
import random


# opti temps mineur: calcul nb arbre dans classe game puis reset game
# opti temps mineur: calcul richness dans map pas de reset
# up richness ?
# créer la valeur (potentielle) d'un seul point de soleil a X timing de la partie et le multiplier par le soleil généré etc
# créer fonction de soleil 


def debug(*args, **kwargs):
    print(*args, **kwargs, file=sys.stderr, flush=True)

class Game:
    def __init__(self, number_of_cells = 37, nutrients = 20, day = 0, sun = 0, score = 0, opp_sun = 0, opp_score = 0, opp_is_waiting = False, number_of_trees = 4, nb_tree_own = 2):
        self.number_of_cells = number_of_cells
        self.nutrients = nutrients
        self.day = day
        self.day_left = 0
        self.sun = sun
        self.score = score
        self.opp_sun = opp_sun
        self.opp_score = opp_score
        self.opp_is_waiting = opp_is_waiting != 0
        self.number_of_trees = number_of_trees
        self.nb_tree_own = nb_tree_own
        self.total_days = 23

class Cell:
    def __init__(self, richness, neighbours, cell, is_dormant = False):
        self.richness = richness
        self.neighbours = neighbours
        self.own = False
        self.size_tree = -1
        self.is_dormant = is_dormant
        self.shadow_potential = {}
        self.cell = cell
        
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

def best_actions(list_actions):
    list = []

    i = 0
    if game.day == 1: #50/50 du debut
        while i < 2:
            tmp = list_actions[i][0].split()
            if tmp[0] == "WAIT":
                break
            for neigh in map[int(tmp[1])].neighbours:
                if neigh >= 0:
                    nb_richness3 = 0
                    for neighboor in map[neigh].neighbours:
                        if neighboor >= 0 and map[neighboor].richness == 3:
                            nb_richness3 += 1
                    if nb_richness3 == 2:
                        return list_actions[i][0]
            i += 1

    i = 0
    while game.sun >= 0:
        tmp = str(list_actions[i][0])
        cost_action = compute_cost_action(tmp)
        if tmp == "WAIT":
            list.append(tmp)
            break
        if game.sun >= cost_action:
            list.append(tmp)
            debug(game.sun)
            game.sun -= cost_action
        i += 1

    for idx, action in enumerate(list):
        action = action.split()
        if action[0] == "COMPLETE":
            return list[idx]
    
    tmp = (0, 0)
    flag = 0
    for idx, action in enumerate(list):
        action = action.split()
        if action[0] == "SEED":
            return list[idx]
        elif (action[0] == "GROW" and map[int(action[1])].size_tree >= tmp[0]):
            tmp = (map[int(action[1])].size_tree, idx)
            flag += 1
    
    if flag > 1:
        return list[tmp[1]]
    else:
        return list[0]

def reset_infos():
    debug("RESET INFO")
    game.nb_tree_own = 0
    for cell in map:
        map[cell].shadowed_by_us = 0
        map[cell].shadowed_by_him = 0
        map[cell].potential_shadowed_by_us = 0
        map[cell].potential_shadowed_by_him = 0
        map[cell].size_tree = -1
        map[cell].own = False
        map[cell].is_dormant = False

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

def compute_cost_action(action):

    def cost_seed(map):
        cost = 0
        for key in dict(map):
            if map[key].size_tree == 0 and map[key].own:
                cost += 1
        return cost

    def cost_grow(map, index):
        debug("taille de l'arbre a grow : ", map[index].size_tree)
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

def calcul_point_richness(cell):
    if map[cell].richness == 1:
        return 0
    elif map[cell].richness == 2:
        return 2       
    elif map[cell].richness == 3:
        return 4    
    else:
        return 0

def seed_heuristique(action):# SEED OK
    
    cell = int(action.split(" ")[2])
    nb_tree = calcul_nb_arbre() #deplacé dans receip info win time ??

    potentiel = game.day_left * 3 - (1 + nb_tree[0]) - (3 + nb_tree[1]) - (7 + nb_tree[2]) - (3 * 3) - (3 * 2) - (3)
    # potentiel = game.day_left * 1 - (1 + nb_tree[0])
    heuristique = 5000

    if map[int(action.split()[1])].size_tree == 1:
        return -1

    own_block = 0
    ennemy_block = 0
    for day in range(6): # ombrage généré supplémentaire
        for dist in range(len(map[cell].shadow_potential[day])):
            if map[map[cell].shadow_potential[day][dist]].size_tree <= 3 and map[map[cell].shadow_potential[day][dist]].size_tree >= 0:
                if map[map[cell].shadow_potential[day][dist]].own:
                    # if map[map[cell].shadow_potential[day][dist]].size_tree >= dist + 1:
                    if map[map[cell].shadow_potential[day][dist]].size_tree >= dist + 1:
                        # own_block += map[map[cell].shadow_potential[day][dist]].size_tree + 1
                        own_block += 7
                    else:
                        own_block += 1 + (((1 / (dist + 1) * map[map[cell].shadow_potential[day][dist]].size_tree) * 7))
                        # own_block += 1
                else:
                    if map[map[cell].shadow_potential[day][dist]].size_tree >= dist + 1:
                        ennemy_block += 1
                    else:
                        ennemy_block += (1 / (dist + 1) * map[map[cell].shadow_potential[day][dist]].size_tree)

    # BUG ICI QUAND POTENTIEL NEGATIF

    debug("own block ==", own_block, "on cell :", cell)
    debug("heu avant ==", potentiel)
    if potentiel > 0:
        heuristique -= (potentiel * own_block / 6 * 2) # les arbres qui nous shadow, on va les shadow aussi donc x2
    elif(nb_tree[1] + nb_tree[0] < nb_tree[2]):
        heuristique += 500
    debug("heu apres ==", heuristique)

    heuristique -= (potentiel * own_block / 6 * 2) # ancienne ligne avant le changement > 0 potentiel



    # heuristique += (potentiel * ennemy_block / 6) # / 2

    heuristique += (calcul_point_richness(cell)) * 3 * (game.day / (game.total_days + 1))# GAME NUTRIENTS
    return heuristique + potentiel

def grow_heuristique(action):
    #en cas d'égalité de 2 grow, check nouveau voisin pour plantation
    nb_tree = calcul_nb_arbre()
    cell = int(action.split()[1])
    heuristique = 0

    if map[cell].size_tree == 0:
        potentiel_loss_sp = (1 + nb_tree[0]) + (3 + nb_tree[1]) + (7 + nb_tree[2]) + (3 * 3) + (3 * 2) + (3)
    elif map[cell].size_tree == 1:
        potentiel_loss_sp = (3 + nb_tree[1]) + (7 + nb_tree[2]) + (3 * 2) + (3)
    elif map[cell].size_tree == 2:
        potentiel_loss_sp = (7 + nb_tree[2]) + 3

     
    potentiel = game.day_left * (3) - potentiel_loss_sp + (game.day_left - 1) * 3

    own_block = 0
    ennemy_block = 0
    for day in range(6): # ombrage généré supplémentaire
        for i in range(len(map[cell].shadow_potential[day])):
            if (map[map[cell].shadow_potential[day][i]].size_tree == map[cell].size_tree or map[map[cell].shadow_potential[day][i]].size_tree == map[cell].size_tree + 1) and i <= map[cell].size_tree:
                if map[map[cell].shadow_potential[day][i]].own:
                    own_block += map[map[cell].shadow_potential[day][i]].size_tree * (day % 6) / 6
                else:
                    ennemy_block += map[map[cell].shadow_potential[day][i]].size_tree * (day % 6) / 6
    
    heuristique = potentiel
    heuristique -= own_block * game.day_left / 6 * 2
    heuristique += (ennemy_block * game.day_left / 6 * 3) #* 3 save + block + snowball

    tmp = days_before_shadowed(cell, game.day)
    map[cell].size_tree += 1
    heuristique += map[cell].size_tree if (days_before_shadowed(cell, game.day) - tmp) > 0 and tmp == 1 else 0 #soleil gagné en le montant maintenant
    heuristique -= map[cell].size_tree if days_before_shadowed(cell, game.day) == 1 else 0
    heuristique += calcul_point_richness(cell) / 4
    map[cell].size_tree -= 1
    if game.day_left > 3 and game.day_left > 0:
        gen_sp_next_turn = nb_tree[0] * 1 + (nb_tree[1] - 1) * 2 + nb_tree[2] * 3 + 3 # + 3 = current tree up - 1 for current
        debug("gen sp next turn", gen_sp_next_turn)
        if map[cell].size_tree == 2 and gen_sp_next_turn >= 4 + (nb_tree[2] * 4):
            heuristique += 1000 * calcul_point_richness(cell)

    return (heuristique / 3) + ( heuristique * ((map[cell].size_tree + 1) / 3) * 2 / 3) 

def complete_heuristique(cell):

    nb_tree = calcul_nb_arbre()

    sum_sp_game_day_left = (3 * game.day_left)
    heuristique = game.nutrients * 3 - sum_sp_game_day_left# point de soleil gagné = nutrients * 3) - (point de soleil non généré)

    # debug("COMPLETE ", cell, "\n", "heuristique =", heuristique, "game.nutrients = ", game.nutrients, "game.day_left = ", game.day_left, "game.day =", game.day)
    benefits_new_seed = game.day_left * 3 - (1 + nb_tree[0]) - (3 + nb_tree[1]) - (7 + nb_tree[2]) - (3 * 3) - (3 * 2) - (3) # perte d'utilisation réel des points de soleil pas utilisé
    if sum_sp_game_day_left > 0: #uniquement si effet snowball positif ?
        heuristique -= (benefits_new_seed / game.day_left * 3) + game.day_left * 3# effet snowball benefits seed =  ((60 - 2 - 6 - 12 - 9 - 6 - 3 / 60) + 60


    own_block = 0
    ennemy_block = 0
    for day in range(6): # ombrage généré supplémentaire
        for i in range(len(map[cell].shadow_potential[day])):
            if map[map[cell].shadow_potential[day][i]].size_tree == map[cell].size_tree:
                if map[map[cell].shadow_potential[day][i]].own:
                    own_block += map[map[cell].shadow_potential[day][i]].size_tree
                else:
                    ennemy_block += map[map[cell].shadow_potential[day][i]].size_tree
    heuristique += (own_block * game.day_left / 6 * 2) # nb de point de soleil qu'on se deny par taille arbre * (temps de deny / 6) * 2(on se bloque 2 fois)
    heuristique -= ennemy_block * game.day_left / 6 # nb de point de soleil qu'on deny par taille arbre * (temps de deny / 6)
    heuristique += map[cell].size_tree if days_before_shadowed(cell, game.day) == 1 else 0 #soleil gagné en le montant maintenant
    heuristique += nb_tree[2] # soleil perdu pour refaire pousser un arbre
    heuristique += (calcul_point_richness(cell)) * 3 * (game.day / (game.total_days + 1)) / 100 #en cas d'égalité
    

    return heuristique

def calcul_heuristique(action):
    list_action = action.split()
    heuristique = 0
    if list_action[0] == "SEED":
        heuristique = seed_heuristique(action) 
        if compute_cost_action(action) > 0: #jamais 2 graines en meme temps
            heuristique = -1
    elif list_action[0] == "GROW":
        heuristique = grow_heuristique(action) / (compute_cost_action(action))
    elif list_action[0] == "COMPLETE":
        heuristique = complete_heuristique(int(list_action[1])) / (compute_cost_action(action))
    return heuristique

def reception_info():
    # general game infos
    reset_infos()
    game.day = int(input())  # the game lasts 24 days: 0-23
    game.nutrients = int(input())  # the base score you gain from the next COMPLETE action
    game.day_left = game.total_days - game.day

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

troll =  [
    'people',
    'history',
    'way',
    'world',
    'information',
    'map',
    'two',
    'family',
    'government',
    'health',
    'system',
    'computer',
    'meat',
    'year',
    'thanks',
    'music',
    'person',
    'reading',
    'method',
    'data',
    'food',
    'understanding',
    'theory',
    'law',
    'bird',
    'literature',
    'problem',
    'software',
    'control',
    'knowledge',
    'power',
    'ability',
    'economics',
    'love',
    'internet',
    'television',
    'science',
    'library',
    'nature',
    'fact',
    'product',
    'idea',
    'temperature',
    'investment',
    'area',
    'society',
    'activity',
    'story',
    'industry',
    'media',
    'thing',
    'oven',
    'community',
    'definition',
    'safety',
    'quality',
    'development',
    'language',
    'management',
    'player',
    'variety',
    'video',
    'week',
    'security',
    'country',
    'exam',
    'movie',
    'organization',
    'equipment',
    'physics',
    'analysis',
    'policy',
    'series',
    'thought',
    'basis',
    'boyfriend',
    'direction',
    'strategy',
    'technology',
    'army',
    'camera',
    'freedom',
    'paper',
    'environment',
    'child',
    'instance',
    'month',
    'truth',
    'marketing',
    'university',
    'writing',
    'article',
    'department',
    'difference',
    'goal',
    'news',
    'audience',
    'fishing',
    'growth',
    'income',
    'marriage',
    'user',
    'combination',
    'failure',
    'meaning',
    'medicine',
    'philosophy',
    'teacher',
    'communication',
    'night',
    'chemistry',
    'disease',
    'disk',
    'energy',
    'nation',
    'road',
    'role',
    'soup',
    'advertising',
    'location',
    'success',
    'addition',
    'apartment',
    'education',
    'math',
    'moment',
    'painting',
    'politics',
    'attention',
    'decision',
    'event',
    'property',
    'shopping',
    'student',
    'wood',
    'competition',
    'distribution',
    'entertainment',
    'office',
    'population',
    'president',
    'unit',
    'category',
    'cigarette',
    'context',
    'introduction',
    'opportunity',
    'performance',
    'driver',
    'flight',
    'length',
    'magazine',
    'newspaper',
    'relationship',
    'teaching',
    'cell',
    'dealer',
    'debate',
    'finding',
    'lake',
    'member',
    'message',
    'phone',
    'scene',
    'appearance',
    'association',
    'concept',
    'customer',
    'death',
    'discussion',
    'housing',
    'inflation',
    'insurance',
    'mood',
    'woman',
    'advice',
    'blood',
    'effort',
    'expression',
    'importance',
    'opinion',
    'payment',
    'reality',
    'responsibility',
    'situation',
    'skill',
    'statement',
    'wealth',
    'application',
    'city',
    'county',
    'depth',
    'estate',
    'foundation',
    'grandmother',
    'heart',
    'perspective',
    'photo',
    'recipe',
    'studio',
    'topic',
    'collection',
    'depression',
    'imagination',
    'passion',
    'percentage',
    'resource',
    'setting',
    'ad',
    'agency',
    'college',
    'connection',
    'criticism',
    'debt',
    'description',
    'memory',
    'patience',
    'secretary',
    'solution',
    'administration',
    'aspect',
    'attitude',
    'director',
    'personality',
    'psychology',
    'recommendation',
    'response',
    'selection',
    'storage',
    'version',
    'alcohol',
    'argument',
    'complaint',
    'contract',
    'emphasis',
    'highway',
    'loss',
    'membership',
    'possession',
    'preparation',
    'steak',
    'union',
    'agreement',
    'cancer',
    'currency',
    'employment',
    'engineering',
    'entry',
    'interaction',
    'limit',
    'mixture',
    'preference',
    'region',
    'republic',
    'seat',
    'tradition',
    'virus',
    'actor',
    'classroom',
    'delivery',
    'device',
    'difficulty',
    'drama',
    'election',
    'engine',
    'football',
    'guidance',
    'hotel',
    'match',
    'owner',
    'priority',
    'protection',
    'suggestion',
    'tension',
    'variation',
    'anxiety',
    'atmosphere',
    'awareness',
    'bread',
    'climate',
    'comparison',
    'confusion',
    'construction',
    'elevator',
    'emotion',
    'employee',
    'employer',
    'guest',
    'height',
    'leadership',
    'mall',
    'manager',
    'operation',
    'recording',
    'respect',
    'sample',
    'transportation',
    'boring',
    'charity',
    'cousin',
    'disaster',
    'editor',
    'efficiency',
    'excitement',
    'extent',
    'feedback',
    'guitar',
    'homework',
    'leader',
    'mom',
    'outcome',
    'permission',
    'presentation',
    'promotion',
    'reflection',
    'refrigerator',
    'resolution',
    'revenue',
    'session',
    'singer',
    'tennis',
    'basket',
    'bonus',
    'cabinet',
    'childhood',
    'church',
    'clothes',
    'coffee',
    'dinner',
    'drawing',
    'hair',
    'hearing',
    'initiative',
    'judgment',
    'lab',
    'measurement',
    'mode',
    'mud',
    'orange',
    'poetry',
    'police',
    'possibility',
    'procedure',
    'queen',
    'ratio',
    'relation',
    'restaurant',
    'satisfaction',
    'sector',
    'signature',
    'significance',
    'song',
    'tooth',
    'town',
    'vehicle',
    'volume',
    'wife',
    'accident',
    'airport',
    'appointment',
    'arrival',
    'assumption',
    'baseball',
    'chapter',
    'committee',
    'conversation',
    'database',
    'enthusiasm',
    'error',
    'explanation',
    'farmer',
    'gate',
    'girl',
    'hall',
    'historian',
    'hospital',
    'injury',
    'instruction',
    'maintenance',
    'manufacturer',
    'meal',
    'perception',
    'pie',
    'poem',
    'presence',
    'proposal',
    'reception',
    'replacement',
    'revolution',
    'river',
    'son',
    'speech',
    'tea',
    'village',
    'warning',
    'winner',
    'worker',
    'writer',
    'assistance',
    'breath',
    'buyer',
    'chest',
    'chocolate',
    'conclusion',
    'contribution',
    'cookie',
    'courage',
    'dad',
    'desk',
    'drawer',
    'establishment',
    'examination',
    'garbage',
    'grocery',
    'honey',
    'impression',
    'improvement',
    'independence',
    'insect',
    'inspection',
    'inspector',
    'king',
    'ladder',
    'menu',
    'penalty',
    'piano',
    'potato',
    'profession',
    'professor',
    'quantity',
    'reaction',
    'requirement',
    'salad',
    'sister',
    'supermarket',
    'tongue',
    'weakness',
    'wedding',
    'affair',
    'ambition',
    'analyst',
    'apple',
    'assignment',
    'assistant',
    'bathroom',
    'bedroom',
    'beer',
    'birthday',
    'celebration',
    'championship',
    'cheek',
    'client',
    'consequence',
    'departure',
    'diamond',
    'dirt',
    'ear',
    'fortune',
    'friendship',
    'funeral',
    'gene',
    'girlfriend',
    'hat',
    'indication',
    'intention',
    'lady',
    'midnight',
    'negotiation',
    'obligation',
    'passenger',
    'pizza',
    'platform',
    'poet',
    'pollution',
    'recognition',
    'reputation',
    'shirt',
    'sir',
    'speaker',
    'stranger',
    'surgery',
    'sympathy',
    'tale',
    'throat',
    'trainer',
    'uncle',
    'youth',
    'time',
    'work',
    'film',
    'water',
    'money',
    'example',
    'while',
    'business',
    'study',
    'game',
    'life',
    'form',
    'air',
    'day',
    'place',
    'number',
    'part',
    'field',
    'fish',
    'back',
    'process',
    'heat',
    'hand',
    'experience',
    'job',
    'book',
    'end',
    'point',
    'type',
    'home',
    'economy',
    'value',
    'body',
    'market',
    'guide',
    'interest',
    'state',
    'radio',
    'course',
    'company',
    'price',
    'size',
    'card',
    'list',
    'mind',
    'trade',
    'line',
    'care',
    'group',
    'risk',
    'word',
    'fat',
    'force',
    'key',
    'light',
    'training',
    'name',
    'school',
    'top',
    'amount',
    'level',
    'order',
    'practice',
    'research',
    'sense',
    'service',
    'piece',
    'web',
    'boss',
    'sport',
    'fun',
    'house',
    'page',
    'term',
    'test',
    'answer',
    'sound',
    'focus',
    'matter',
    'kind',
    'soil',
    'board',
    'oil',
    'picture',
    'access',
    'garden',
    'range',
    'rate',
    'reason',
    'future',
    'site',
    'demand',
    'exercise',
    'image',
    'case',
    'cause',
    'coast',
    'action',
    'age',
    'bad',
    'boat',
    'record',
    'result',
    'section',
    'building',
    'mouse',
    'cash',
    'class',
    'nothing',
    'period',
    'plan',
    'store',
    'tax',
    'side',
    'subject',
    'space',
    'rule',
    'stock',
    'weather',
    'chance',
    'figure',
    'man',
    'model',
    'source',
    'beginning',
    'earth',
    'program',
    'chicken',
    'design',
    'feature',
    'head',
    'material',
    'purpose',
    'question',
    'rock',
    'salt',
    'act',
    'birth',
    'car',
    'dog',
    'object',
    'scale',
    'sun',
    'note',
    'profit',
    'rent',
    'speed',
    'style',
    'war',
    'bank',
    'craft',
    'half',
    'inside',
    'outside',
    'standard',
    'bus',
    'exchange',
    'eye',
    'fire',
    'position',
    'pressure',
    'stress',
    'advantage',
    'benefit',
    'box',
    'frame',
    'issue',
    'step',
    'cycle',
    'face',
    'item',
    'metal',
    'paint',
    'review',
    'room',
    'screen',
    'structure',
    'view',
    'account',
    'ball',
    'discipline',
    'medium',
    'share',
    'balance',
    'bit',
    'black',
    'bottom',
    'choice',
    'gift',
    'impact',
    'machine',
    'shape',
    'tool',
    'wind',
    'address',
    'average',
    'career',
    'culture',
    'morning',
    'pot',
    'sign',
    'table',
    'task',
    'condition',
    'contact',
    'credit',
    'egg',
    'hope',
    'ice',
    'network',
    'north',
    'square',
    'attempt',
    'date',
    'effect',
    'link',
    'post',
    'star',
    'voice',
    'capital',
    'challenge',
    'friend',
    'self',
    'shot',
    'brush',
    'couple',
    'exit',
    'front',
    'function',
    'lack',
    'living',
    'plant',
    'plastic',
    'spot',
    'summer',
    'taste',
    'theme',
    'track',
    'wing',
    'brain',
    'button',
    'click',
    'desire',
    'foot',
    'gas',
    'influence',
    'notice',
    'rain',
    'wall',
    'base',
    'damage',
    'distance',
    'feeling',
    'pair',
    'savings',
    'staff',
    'sugar',
    'target',
    'text',
    'animal',
    'author',
    'budget',
    'discount',
    'file',
    'ground',
    'lesson',
    'minute',
    'officer',
    'phase',
    'reference',
    'register',
    'sky',
    'stage',
    'stick',
    'title',
    'trouble',
    'bowl',
    'bridge',
    'campaign',
    'character',
    'club',
    'edge',
    'evidence',
    'fan',
    'letter',
    'lock',
    'maximum',
    'novel',
    'option',
    'pack',
    'park',
    'plenty',
    'quarter',
    'skin',
    'sort',
    'weight',
    'baby',
    'background',
    'carry',
    'dish',
    'factor',
    'fruit',
    'glass',
    'joint',
    'master',
    'muscle',
    'red',
    'strength',
    'traffic',
    'trip',
    'vegetable',
    'appeal',
    'chart',
    'gear',
    'ideal',
    'kitchen',
    'land',
    'log',
    'mother',
    'net',
    'party',
    'principle',
    'relative',
    'sale',
    'season',
    'signal',
    'spirit',
    'street',
    'tree',
    'wave',
    'belt',
    'bench',
    'commission',
    'copy',
    'drop',
    'minimum',
    'path',
    'progress',
    'project',
    'sea',
    'south',
    'status',
    'stuff',
    'ticket',
    'tour',
    'angle',
    'blue',
    'breakfast',
    'confidence',
    'daughter',
    'degree',
    'doctor',
    'dot',
    'dream',
    'duty',
    'essay',
    'father',
    'fee',
    'finance',
    'hour',
    'juice',
    'luck',
    'milk',
    'mouth',
    'peace',
    'pipe',
    'stable',
    'storm',
    'substance',
    'team',
    'trick',
    'afternoon',
    'bat',
    'beach',
    'blank',
    'catch',
    'chain',
    'consideration',
    'cream',
    'crew',
    'detail',
    'gold',
    'interview',
    'kid',
    'mark',
    'mission',
    'pain',
    'pleasure',
    'score',
    'screw',
    'sex',
    'shop',
    'shower',
    'suit',
    'tone',
    'window',
    'agent',
    'band',
    'bath',
    'block',
    'bone',
    'calendar',
    'candidate',
    'cap',
    'coat',
    'contest',
    'corner',
    'court',
    'cup',
    'district',
    'door',
    'east',
    'finger',
    'garage',
    'guarantee',
    'hole',
    'hook',
    'implement',
    'layer',
    'lecture',
    'lie',
    'manner',
    'meeting',
    'nose',
    'parking',
    'partner',
    'profile',
    'rice',
    'routine',
    'schedule',
    'swimming',
    'telephone',
    'tip',
    'winter',
    'airline',
    'bag',
    'battle',
    'bed',
    'bill',
    'bother',
    'cake',
    'code',
    'curve',
    'designer',
    'dimension',
    'dress',
    'ease',
    'emergency',
    'evening',
    'extension',
    'farm',
    'fight',
    'gap',
    'grade',
    'holiday',
    'horror',
    'horse',
    'host',
    'husband',
    'loan',
    'mistake',
    'mountain',
    'nail',
    'noise',
    'occasion',
    'package',
    'patient',
    'pause',
    'phrase',
    'proof',
    'race',
    'relief',
    'sand',
    'sentence',
    'shoulder',
    'smoke',
    'stomach',
    'string',
    'tourist',
    'towel',
    'vacation',
    'west',
    'wheel',
    'wine',
    'arm',
    'aside',
    'associate',
    'bet',
    'blow',
    'border',
    'branch',
    'breast',
    'brother',
    'buddy',
    'bunch',
    'chip',
    'coach',
    'cross',
    'document',
    'draft',
    'dust',
    'expert',
    'floor',
    'god',
    'golf',
    'habit',
    'iron',
    'judge',
    'knife',
    'landscape',
    'league',
    'mail',
    'mess',
    'native',
    'opening',
    'parent',
    'pattern',
    'pin',
    'pool',
    'pound',
    'request',
    'salary',
    'shame',
    'shelter',
    'shoe',
    'silver',
    'tackle',
    'tank',
    'trust',
    'assist',
    'bake',
    'bar',
    'bell',
    'bike',
    'blame',
    'boy',
    'brick',
    'chair',
    'closet',
    'clue',
    'collar',
    'comment',
    'conference',
    'devil',
    'diet',
    'fear',
    'fuel',
    'glove',
    'jacket',
    'lunch',
    'monitor',
    'mortgage',
    'nurse',
    'pace',
    'panic',
    'peak',
    'plane',
    'reward',
    'row',
    'sandwich',
    'shock',
    'spite',
    'spray',
    'surprise',
    'till',
    'transition',
    'weekend',
    'welcome',
    'yard',
    'alarm',
    'bend',
    'bicycle',
    'bite',
    'blind',
    'bottle',
    'cable',
    'candle',
    'clerk',
    'cloud',
    'concert',
    'counter',
    'flower',
    'grandfather',
    'harm',
    'knee',
    'lawyer',
    'leather',
    'load',
    'mirror',
    'neck',
    'pension',
    'plate',
    'purple',
    'ruin',
    'ship',
    'skirt',
    'slice',
    'snow',
    'specialist',
    'stroke',
    'switch',
    'trash',
    'tune',
    'zone',
    'anger',
    'award',
    'bid',
    'bitter',
    'boot',
    'bug',
    'camp',
    'candy',
    'carpet',
    'cat',
    'champion',
    'channel',
    'clock',
    'comfort',
    'cow',
    'crack',
    'engineer',
    'entrance',
    'fault',
    'grass',
    'guy',
    'hell',
    'highlight',
    'incident',
    'island',
    'joke',
    'jury',
    'leg',
    'lip',
    'mate',
    'motor',
    'nerve',
    'passage',
    'pen',
    'pride',
    'priest',
    'prize',
    'promise',
    'resident',
    'resort',
    'ring',
    'roof',
    'rope',
    'sail',
    'scheme',
    'script',
    'sock',
    'station',
    'toe',
    'tower',
    'truck',
    'witness',
    'a',
    'you',
    'it',
    'can',
    'will',
    'if',
    'one',
    'many',
    'most',
    'other',
    'use',
    'make',
    'good',
    'look',
    'help',
    'go',
    'great',
    'being',
    'few',
    'might',
    'still',
    'public',
    'read',
    'keep',
    'start',
    'give',
    'human',
    'local',
    'general',
    'she',
    'specific',
    'long',
    'play',
    'feel',
    'high',
    'tonight',
    'put',
    'common',
    'set',
    'change',
    'simple',
    'past',
    'big',
    'possible',
    'particular',
    'today',
    'major',
    'personal',
    'current',
    'national',
    'cut',
    'natural',
    'physical',
    'show',
    'try',
    'check',
    'second',
    'call',
    'move',
    'pay',
    'let',
    'increase',
    'single',
    'individual',
    'turn',
    'ask',
    'buy',
    'guard',
    'hold',
    'main',
    'offer',
    'potential',
    'professional',
    'international',
    'travel',
    'cook',
    'alternative',
    'following',
    'special',
    'working',
    'whole',
    'dance',
    'excuse',
    'cold',
    'commercial',
    'low',
    'purchase',
    'deal',
    'primary',
    'worth',
    'fall',
    'necessary',
    'positive',
    'produce',
    'search',
    'present',
    'spend',
    'talk',
    'creative',
    'tell',
    'cost',
    'drive',
    'green',
    'support',
    'glad',
    'remove',
    'return',
    'run',
    'complex',
    'due',
    'effective',
    'middle',
    'regular',
    'reserve',
    'independent',
    'leave',
    'original',
    'reach',
    'rest',
    'serve',
    'watch',
    'beautiful',
    'charge',
    'active',
    'break',
    'negative',
    'safe',
    'stay',
    'visit',
    'visual',
    'affect',
    'cover',
    'report',
    'rise',
    'walk',
    'white',
    'beyond',
    'junior',
    'pick',
    'unique',
    'anything',
    'classic',
    'final',
    'lift',
    'mix',
    'private',
    'stop',
    'teach',
    'western',
    'concern',
    'familiar',
    'fly',
    'official',
    'broad',
    'comfortable',
    'gain',
    'maybe',
    'rich',
    'save',
    'stand',
    'young',
    'heavy',
    'hello',
    'lead',
    'listen',
    'valuable',
    'worry',
    'handle',
    'leading',
    'meet',
    'release',
    'sell',
    'finish',
    'normal',
    'press',
    'ride',
    'secret',
    'spread',
    'spring',
    'tough',
    'wait',
    'brown',
    'deep',
    'display',
    'flow',
    'hit',
    'objective',
    'shoot',
    'touch',
    'cancel',
    'chemical',
    'cry',
    'dump',
    'extreme',
    'push',
    'conflict',
    'eat',
    'fill',
    'formal',
    'jump',
    'kick',
    'opposite',
    'pass',
    'pitch',
    'remote',
    'total',
    'treat',
    'vast',
    'abuse',
    'beat',
    'burn',
    'deposit',
    'print',
    'raise',
    'sleep',
    'somewhere',
    'advance',
    'anywhere',
    'consist',
    'dark',
    'double',
    'draw',
    'equal',
    'fix',
    'hire',
    'internal',
    'join',
    'kill',
    'sensitive',
    'tap',
    'win',
    'attack',
    'claim',
    'constant',
    'drag',
    'drink',
    'guess',
    'minor',
    'pull',
    'raw',
    'soft',
    'solid',
    'wear',
    'weird',
    'wonder',
    'annual',
    'count',
    'dead',
    'doubt',
    'feed',
    'forever',
    'impress',
    'nobody',
    'repeat',
    'round',
    'sing',
    'slide',
    'strip',
    'whereas',
    'wish',
    'combine',
    'command',
    'dig',
    'divide',
    'equivalent',
    'hang',
    'hunt',
    'initial',
    'march',
    'mention',
    'spiritual',
    'survey',
    'tie',
    'adult',
    'brief',
    'crazy',
    'escape',
    'gather',
    'hate',
    'prior',
    'repair',
    'rough',
    'sad',
    'scratch',
    'sick',
    'strike',
    'employ',
    'external',
    'hurt',
    'illegal',
    'laugh',
    'lay',
    'mobile',
    'nasty',
    'ordinary',
    'respond',
    'royal',
    'senior',
    'split',
    'strain',
    'struggle',
    'swim',
    'train',
    'upper',
    'wash',
    'yellow',
    'convert',
    'crash',
    'dependent',
    'fold',
    'funny',
    'grab',
    'hide',
    'miss',
    'permit',
    'quote',
    'recover',
    'resolve',
    'roll',
    'sink',
    'slip',
    'spare',
    'suspect',
    'sweet',
    'swing',
    'twist',
    'upstairs',
    'usual',
    'abroad',
    'brave',
    'calm',
    'concentrate',
    'estimate',
    'grand',
    'male',
    'mine',
    'prompt',
    'quiet',
    'refuse',
    'regret',
    'reveal',
    'rush',
    'shake',
    'shift',
    'shine',
    'steal',
    'suck',
    'surround',
    'anybody',
    'bear',
    'brilliant',
    'dare',
    'dear',
    'delay',
    'drunk',
    'female',
    'hurry',
    'inevitable',
    'invite',
    'kiss',
    'neat',
    'pop',
    'punch',
    'quit',
    'reply',
    'representative',
    'resist',
    'rip',
    'rub',
    'silly',
    'smile',
    'spell',
    'stretch',
    'stupid',
    'tear',
    'temporary',
    'tomorrow',
    'wake',
    'wrap',
    'yesterday',
]

if __name__ == "__main__":
    game = Game()
    game.number_of_cells = int(input())

    # map info
    map = {}
    for i in range(game.number_of_cells):
        index, richness, neigh_0, neigh_1, neigh_2, neigh_3, neigh_4, neigh_5 = [int(j) for j in input().split()]
        map[index] = Cell(richness, (neigh_0, neigh_1, neigh_2, neigh_3, neigh_4, neigh_5), index)

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

        list_actions = sorted(list_actions, key=lambda x: x[1], reverse= True)
        for action in list_actions:
            if action[1] > -1:
                debug("Action : ", action[0], " -- Heuristique : ", action[1], "\n")
        best_action = best_actions(list_actions)

        print(best_action, " ".join([troll[random.randrange(0, len(troll))] for i in range(3)]) + " " + str(random.randint(-10,100)))


    # Write an action using print
    # To debug: print("Debug messages...", file=sys.stderr, flush=True)


    # GROW cellIdx | SEED sourceIdx targetIdx | COMPLETE cellIdx | WAIT <message>