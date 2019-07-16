import networkx as nx

from NetworkXGeo import add_nodes
from SrtLinks import connect_graph
from neo4j_to_networkx import get_nodes_from_db, add_rels, get_rels_from_db


# def draw_graph(graph):
#     nx.draw_networkx(G=graph)


if __name__ == '__main__':
    G = nx.dodecahedral_graph()
    nx.draw(G)
    # neo4j_graph = connect_graph()
    # G = nx.MultiDiGraph()
    # add_nodes(G, get_nodes_from_db(neo4j_graph))
    # add_rels(G, get_rels_from_db(neo4j_graph))
    #
    # draw_graph(G)
