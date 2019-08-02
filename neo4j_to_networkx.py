import time
import itertools
import uuid

from itertools import islice
from pprint import pprint

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
            time=rel['length']*60/rel['speed'],
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
    penalties = get_penalties_data()  # данные о штрафах из файла
    # coordinate_nodes = get_nodes_by_attr_value(graph, key='type', value='coord')

    coordinate_nodes = [(x, y) for x, y in graph.nodes(data=True) if y['type'] == 'coord']
    coordinate_edges = list(graph.edges())

    print('CREATING PENALTIES NODES AND EDGES..')
    for node in coordinate_nodes:
        in_edges = list(graph.in_edges(node[0], data=True))[
                   :]  # для каждой координатной точки ищем входящие и выходящие ребра
        out_edges = list(graph.out_edges(node[0], data=True))[:]

        in_edges_coords = [edge for edge in in_edges if (isinstance(edge[0], int) and isinstance(edge[1], int))]
        out_edges_coords = [edge for edge in out_edges if (isinstance(edge[0], int) and isinstance(edge[1], int))]

        edge_pairs = list(itertools.product(in_edges, out_edges))  # находим пары ребер

        edge_pair_id = 1
        # if not in_edges:
        #     graph.add_node(f'{node[0]}_out_{edge_pair_id}', node_pk=node[0], type='penalty_node')
        #
        #     for out_edge in out_edges:
        #         graph.add_edge(f'{node[0]}_out_{edge_pair_id}', out_edge[1])
        #         graph.remove_edge(out_edge[0], out_edge[1])
        #     continue
        #
        # elif not out_edges:
        #     graph.add_node(f'{node[0]}_in_{edge_pair_id}', node_pk=node[0], type='penalty_node')
        #     for out_edge in out_edges:
        #         graph.add_edge(f'{node[0]}_out_{edge_pair_id}', out_edge[0])
        #         graph.remove_edge(out_edge[0], out_edge[1])
        #     continue

        for edge_pair in edge_pairs:
            edge_pair_id += 1
            in_edge_link_type = edge_pair[0][2]['link_type_id']
            out_edge_link_type = edge_pair[1][2]['link_type_id']
            graph.add_node(f'{node[0]}_in_{edge_pair_id}', node_pk=node[0], type='penalty_node')
            graph.add_node(f'{node[0]}_out_{edge_pair_id}', node_pk=node[0], type='penalty_node')

            in_edge_data = {'node_id_from': edge_pair[0][0], 'node_id_to': edge_pair[0][1], **edge_pair[0][2]}
            out_edge_data = {'node_id_from': edge_pair[1][0], 'node_id_to': edge_pair[1][1], **edge_pair[1][2]}

            for data in penalties:
                if [in_edge_link_type, out_edge_link_type] == [data['link_type_id_1'], data['link_type_id_2']]:
                    # and data['normal_penalty'] != 0:
                    graph.add_edge(f'{node[0]}_in_{edge_pair_id}', f'{node[0]}_out_{edge_pair_id}',
                                   time=data['normal_penalty'], type='penalty_edge')
                    graph.add_edge(edge_pair[0][0], f'{node[0]}_in_{edge_pair_id}', **in_edge_data)
                    graph.add_edge(f'{node[0]}_out_{edge_pair_id}', edge_pair[1][1], **out_edge_data)
                    break

    print('REMOVING COORDINATE EDGES...')
    graph.remove_edges_from(coordinate_edges)

    print('OBTAINING DUPLICATES...')
    all_edges = list(graph.edges(data=True))
    all_edges_no_data = list(graph.edges())
    duplicate_edges_in = [edge for edge in all_edges if isinstance(edge[0], int)]
    duplicate_edges_out = [edge for edge in all_edges if isinstance(edge[1], int)]

    duplicate_edges_out2 = [(int(edge_out[0].split('_')[0]), edge_out[1], edge_out[2]) for edge_out in duplicate_edges_out]

    print('CREATING PROPER EDGES...')
    for edge_in in duplicate_edges_in:
        first_node = edge_in[0]
        second_node = int(edge_in[1].split('_')[0])
        duplicate_check_edge = (first_node, second_node, edge_in[2])
        if duplicate_check_edge in duplicate_edges_out2:
            edge_out = duplicate_edges_out[duplicate_edges_out2.index(duplicate_check_edge)]
            graph.add_edge(edge_out[0], edge_in[1], **edge_in[2])

    print('REMOVING DUPLICATES...')
    graph.remove_edges_from([edge for edge in all_edges_no_data if isinstance(edge[0], int)])
    graph.remove_edges_from([edge for edge in all_edges_no_data if isinstance(edge[1], int)])


def get_shortest_path(graph, node_pk_from, node_pk_to):
    nodes_from = [(node_pk_from, x, {'time': 0}) for x, y in graph.nodes(data=True) if f'{node_pk_from}_out' in str(x)]
    nodes_to = [(x, node_pk_to, {'time': 0}) for x, y in graph.nodes(data=True) if f'{node_pk_to}_in' in str(x)]
    print('ADDING SECONDARY EDGES...')
    graph.add_edges_from(nodes_from)
    graph.add_edges_from(nodes_to)

    print('COMPUTING SHORTEST PATH...')
    path = nx.shortest_path(graph, node_pk_from, node_pk_to, weight='time')

    print('REMOVING SECONDARY EDGES...')
    # graph.remove_edges_from(nodes_from)
    # graph.remove_edges_from(nodes_to)

    return path

    # node_pairs = list(itertools.product(nodes_from, nodes_to))

    # shortest_paths = []
    # for node_pair in node_pairs:
    #     try:
    #         sp = nx.shortest_path(graph, node_pair[0], node_pair[1], weight=time)
    #         shortest_paths.append(sp)
    #     except Exception:
    #         continue
    #
    # return max(shortest_paths)


if __name__ == '__main__':
    neo4j_graph = connect_graph()
    G = nx.MultiDiGraph()

    print('ADDING NODES FROM DATABASE...')
    add_nodes(G, get_nodes_from_db(neo4j_graph))
    print('ADDING EDGES FROM DATABASE...')
    add_rels(G, get_rels_from_db(neo4j_graph))

    print('edges', G.number_of_edges())
    print('nodes', G.number_of_nodes())

    print('ADDING PENALTIES...')
    add_penalties(G)

    print('edges', G.number_of_edges())
    print('nodes', G.number_of_nodes())

    # print('COMPUTING SHORTEST PATH:')
    # shortest_path = nx.shortest_path(G, 4654, 12015, weight='time')
    shortest_path = get_shortest_path(G, 4654, 12015)

    print('shortest path', shortest_path)

    edgesinpath = zip(shortest_path[0:], shortest_path[1:])

    edges = []
    times = []
    for s, t in edgesinpath:
        try:
            node_edges = list(G.edges([s, t], data=True))
            # for u, v in node_edges:

            edge = sorted(node_edges, key=lambda x: x[2]['time'])[0]

            edges.append(edge)
            if edge[2]['type'] == 'penalty_edge':
                times[-1] += edge[2]['time']
            else:
                times.append(edge[2]['time'])
        except IndexError:
            continue
    print('edge times: ', times)

    # nodes_path = []
    # for index, node in enumerate(shortest_path):
    #     try:
    #         node_edges = G.edges([node, shortest_path[index+1]], data=True)
    #         for u, v in node_edges:
    #             edge = sorted(G[u][v], key=lambda x: G[u][v][x]['time'])[0]
    #
    #         edges.append(edge)
    #         if edge['type'] == 'penalty_edge':
    #             times[:-1] += edge['time']
    #         else:
    #             times.append(edge['time'])
    #     except IndexError:
    #         continue
    #     # print(G.edges[node, shortest_path[index+1]])
    #     # edges.append(G.edges([node, shortest_path[index+1]], data=True)['time'])
    # print(times)

    # nodes_path = []
    # for node in shortest_path:
    #     if isinstance(node, str):
    #         node_id = node.split('_')[0]
    #         nodes_path.append(int(node_id))
    #     else:
    #         nodes_path.append(node)
    #
    # print('shortest path: ', (list(dict.fromkeys(nodes_path))))

    # path = nx.shortest_path(G, 4641, 12045, weight='time')
    # print("--- %s seconds ---" % (time.time() - start_time))
    # # print(list(path))
