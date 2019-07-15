from itertools import islice

import networkx as nx


# ПРОБЛЕМА: не работает с MultiGraph почему-то
# Обсудить, насколько это важно

def k_shortest_paths(G, source, target, k, weight=None):
    return list(islice(nx.shortest_simple_paths(G, source, target, weight=weight), k))
