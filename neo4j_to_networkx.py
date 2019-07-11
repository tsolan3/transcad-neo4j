import time
from py2neo import Graph, NodeMatcher, RelationshipMatcher
import networkx as nx


def connect_graph():
    graph = Graph("http://localhost:7474/db/data/", user='neo4j', password='119678Qq')
    return graph


def get_nodes_from_db(graph):
    graph = connect_graph()
    matcher = NodeMatcher(graph)
    nodes = list(matcher.match('COORDINATE'))

    nodes_data = []
    for node in nodes:
        node_json = {'longitude': node['longitude'], 'latitude': node['latitude'], 'pk': node.identity}
        nodes_data.append(node_json)

    return nodes_data


def get_rels_from_db(graph):
    graph = connect_graph()
    matcher = RelationshipMatcher(graph)
    relationships = list(matcher.match())

    rel_data = []
    for rel in relationships:
        rel_json = {
            'direction': rel['direction'],
            'length': rel['length'],
            'is_tram': rel['is_tram'],
            'is_bus': rel['is_bus'],
            'is_trolleybus': rel['is_trolleybus'],
            'is_connector': rel['is_connector'],
            'link_type_id': rel['link_type_id'],
            'pedestrian_mode_id': rel['pedestrian_mode_id'],
            'move_time': rel['move_time'],
            'walking_time': rel['walking_time'],
            'null_time': rel['null_time'],
            'time_bus': rel['time_bus'],
            'time_tram': rel['time_tram'],
            'speed': rel['speed'],
            'node_id_from': rel.start_node.identity,
            'node_id_to': rel.end_node.identity
        }
        rel_data.append(rel_json)

    return rel_data


def add_nodes(G, nodes_data):
    for node in nodes_data:
        G.add_node(node['pk'], longitude=node['longitude'], latitude=node['latitude'])
    return True


def add_rels(G, rel_data):
    for rel in rel_data:
        G.add_edge(
            rel['node_id_from'], rel['node_id_to'],
            length=rel['length'],
            move_time=rel['move_time'],
            is_tram=rel['is_tram'],
            is_bus=rel['is_bus'],
            is_trolleybus=rel['is_trolleybus'],
            is_connector=rel['is_connector'],
            link_type_id=rel['link_type_id'],
            walking_time=rel['walking_time'],
            null_time=rel['null_time'],
            time_bus=rel['time_bus'],
            time_tram=rel['time_tram'],
            speed=rel['speed']
        )
    return True


if __name__ == '__main__':
    neo4j_graph = connect_graph()
    G = nx.MultiDiGraph()
    add_nodes(G, get_nodes_from_db(neo4j_graph))
    add_rels(G, get_rels_from_db(neo4j_graph))

    print(G.number_of_edges())
    print(G.number_of_nodes())
    start_time = time.time()
    print(nx.shortest_path(G, 4641, 12045, weight='length'))
    print("--- %s seconds ---" % (time.time() - start_time))

