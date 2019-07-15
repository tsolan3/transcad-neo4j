from py2neo import Graph, NodeMatcher
import networkx as nx

from neo4j_to_networkx import get_rels_from_db, add_nodes, add_rels


def connect_graph():
    graph = Graph("http://localhost:7474/db/data/", user='neo4j', password='119678Qq')
    return graph


def get_sites():
    with open('transcad_data/SiteToSite2023.csv', 'r') as f:
        json_data = []
        for line in f.readlines():
            data = line.split(',')
            # if data[0] != '' or data[1]
            json_obj = {'node_id_from': int(data[0]), 'node_id_to': int(data[1])}
            json_data.append(json_obj)

    return json_data


def get_nodes_from_db(graph):
    graph = connect_graph()
    matcher = NodeMatcher(graph)
    nodes = list(matcher.match('COORDINATE'))

    nodes_data = []
    for node in nodes:
        node_json = {'longitude': node['longitude'], 'latitude': node['latitude'], 'pk': node['pk']}
        nodes_data.append(node_json)

    return nodes_data

if __name__ == '__main__':
    neo4j_graph = connect_graph()
    G = nx.MultiDiGraph()
    add_nodes(G, get_nodes_from_db(neo4j_graph))
    add_rels(G, get_rels_from_db(neo4j_graph))

    site_pairs = get_sites()
    for site_pair in site_pairs:
        node_id_from = site_pair['node_id_from']
        node_id_to = site_pair['node_id_to']
        try:
            path = nx.shortest_path_length(G, node_id_from, node_id_to, weight='time')
            print(node_id_from, node_id_to)
        except Exception as e:
            print(e)
            continue
