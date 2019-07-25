import time
import itertools
import uuid

from itertools import islice
from pprint import pprint

from py2neo import Graph, NodeMatcher, RelationshipMatcher
import networkx as nx
import matplotlib.pyplot as plt
import gmplot

from utils import get_nodes_by_attr_value


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
        G.add_node(node['pk'], longitude=node['longitude'], latitude=node['latitude'],
                   node_pk=node['pk'], type='coord')
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
            speed=rel['speed'],
            time=rel['length']/rel['speed'],
            type='link'
        )
    return True


def get_penalties_data():
    with open('transcad_data/penalties.csv', 'r') as f:
        json_data = []
        for line in f.readlines():
            data = line.split(',')
            # if data[0] != '' or data[1]
            json_obj = {'link_type_id_1': int(data[0]), 'link_type_id_2': int(data[1]),
                        'normal_penalty': int(data[2]), 'u_turn_penalty': int(data[3])}
            json_data.append(json_obj)
        return json_data


def add_penalties(graph):
        #  получаем все координатные узлы
        # penalties = get_penalties_data()  # данные о штрафах из файла

        coordinate_nodes = [(x, y) for x, y in graph.nodes(data=True) if y['type'] == 'coord']

        # для каждой координатной точки ищем входящие и выходящие ребра и составляем пары
        for node in coordinate_nodes:
            in_edges = list(graph.in_edges(node[0], data=True))[:]
            out_edges = list(graph.out_edges(node[0], data=True))[:]
            edge_pairs = list(itertools.product(in_edges, out_edges))  # находим пары ребер

            # если у точки нет входящих/выходящих потоков (т.е. нет пар ребер)
            edge_pair_id = 1
            if not in_edges:
                graph.add_node(f'{node[0]}_out_{edge_pair_id}', node_pk=node[0], type='penalty_node')

                for out_edge in out_edges:
                    graph.add_edge(f'{node[0]}_out_{edge_pair_id}', out_edge[1])
                    graph.remove_edge(out_edge[0], out_edge[1])
                continue

            elif not out_edges:
                graph.add_node(f'{node[0]}_in_{edge_pair_id}', node_pk=node[0], type='penalty_node')
                for out_edge in out_edges:
                    graph.add_edge(f'{node[0]}_out_{edge_pair_id}', out_edge[0])
                    graph.remove_edge(out_edge[0], out_edge[1])
                continue

            for edge_pair in edge_pairs:
                edge_pair_id += 1

                # это точно делаем
                graph.add_node(f'{node[0]}_in_{edge_pair_id}', node_pk=node[0], type='penalty_node')
                graph.add_node(f'{node[0]}_out_{edge_pair_id}', node_pk=node[0], type='penalty_node')
                #             graph.add_edge(f'{node[0]}_in_{edge_pair_id}', f'{node[0]}_out_{edge_pair_id}',
                #                            time=1.5, type='penalty_edge') # штрафное ребро
                #             graph.add_edge(edge_pair[0][0], f'{node[0]}_in_{edge_pair_id}', **edge_pair[0][2])
                #             graph.add_edge(f'{node[0]}_out_{edge_pair_id}', edge_pair[1][1], **edge_pair[1][2])

                # ТЕПЕРЬ НУЖНО


                #         graph.remove_node(node[0])

                #     for node in coordinate_nodes:
                #         graph.remove_node(node[0])
                #         graph.add_node(node[0], **node[1])


def add_penalties(graph):

    penalties = get_penalties_data()  # данные о штрафах из файла
    # coordinate_nodes = get_nodes_by_attr_value(graph, key='type', value='coord')

    coordinate_nodes = [(x, y) for x, y in graph.nodes(data=True) if y['type'] == 'coord']

    for node in coordinate_nodes:
        in_edges = graph.in_edges(node[0], data=True)  # для каждой координатной точки ищем входящие и выходящие ребра
        out_edges = graph.out_edges(node[0], data=True)
        edge_pairs = list(itertools.product(in_edges, out_edges))  # находим пары ребер

        edge_pair_id = 0
        for edge_pair in edge_pairs:
            edge_pair_id += 1
            in_edge_link_type = edge_pair[0][2]['link_type_id']
            out_edge_link_type = edge_pair[1][2]['link_type_id']

            for data in penalties:
                if [in_edge_link_type, out_edge_link_type] == [data['link_type_id_1'], data['link_type_id_2']]:
                        # and data['normal_penalty'] != 0:

                    graph.add_node(f'{node[0]}_in_{edge_pair_id}', node_pk=node[0], type='penalty_node')
                    graph.add_node(f'{node[0]}_out_{edge_pair_id}', node_pk=node[0], type='penalty_node')

                    graph.add_edge(f'{node[0]}_in_{edge_pair_id}', f'{node[0]}_out_{edge_pair_id}',
                                   time=data['normal_penalty'], type='penalty_edge')
                    graph.add_edge(edge_pair[0][0], f'{node[0]}_{edge_pair_id}_1', **edge_pair[0][2])
                    graph.add_edge(f'{node[0]}_{edge_pair_id}_2', edge_pair[1][1], **edge_pair[1][2])

        graph.remove_node(node[0])
    # pprint(list(graph.edges(data=True)))


def get_shortest_path(graph, node_pk_from, node_pk_to):
    nodes_from = [x for x, y in graph.nodes(data=True) if f'{node_pk_from}_out' in x]
    nodes_to = [x for x, y in graph.nodes(data=True) if f'{node_pk_to}_in' in x]
    node_pairs = list(itertools.product(nodes_from, nodes_to))

    shortest_paths = []
    for node_pair in node_pairs:
        try:
            sp = nx.shortest_path(graph, node_pair[0], node_pair[1], weight=time)
            shortest_paths.append(sp)
        except Exception:
            continue

    return max(shortest_paths)


if __name__ == '__main__':
    neo4j_graph = connect_graph()
    G = nx.MultiDiGraph()


    add_nodes(G, get_nodes_from_db(neo4j_graph))
    add_rels(G, get_rels_from_db(neo4j_graph))

    print('edges', G.number_of_edges())
    print('nodes', G.number_of_nodes())

    add_penalties(G)

    print('edges', G.number_of_edges())
    print('nodes', G.number_of_nodes())

    # start_time = time.time()
    # print(get_shortest_path(G, 4641, 12045))
    # # path = nx.shortest_path(G, 4641, 12045, weight='time')
    # print("--- %s seconds ---" % (time.time() - start_time))
    # # print(list(path))



