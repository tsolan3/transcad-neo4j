import itertools
import networkx as nx


#
# from neo4j_to_networkx import get_penalties_data
#
#
# def add_penalty_edges(graph):
#     penalties = get_penalties_data()  # данные о штрафах из файла
#     coordinate_nodes = list(graph.nodes)[:]  # получаем все координатные узлы и делаем копию на всякий случай
#     for node in coordinate_nodes:
#         in_edges = graph.in_edges(node, data=True)  # для каждой координатной точки ищем входящие и выходящие ребра
#         out_edges = graph.out_edges(node, data=True)
#         edge_pairs = list(itertools.product(in_edges, out_edges))  # находим пары ребер
#         for edge_pair in edge_pairs:
#             in_edge_link_type = edge_pair[0][2]['link_type_id']
#             out_edge_link_type = edge_pair[1][2]['link_type_id']
#             for data in penalties:
#                 if [in_edge_link_type, out_edge_link_type] == [data['link_type_id_1'], data['link_type_id_2']]:
#                         # and data['normal_penalty'] != 0:
#                     graph.add_edge(node, node, time=data['normal_penalty'], type='penalty')

def add_penalties(graph):
    coordinate_nodes = [(x, y) for x, y in graph.nodes(data=True) if y['type'] == 'coord']

    for node in coordinate_nodes:
        in_edges = graph.in_edges(node[0], data=True)  # для каждой координатной точки ищем входящие и выходящие ребра
        out_edges = graph.out_edges(node[0], data=True)
        edge_pairs = list(itertools.product(in_edges, out_edges))  # находим пары ребер

        edge_pair_id = 0
        if not in_edges:
            graph.add_node(f'{node[0]}_out_{edge_pair_id}', node_pk=node[0], type='penalty_node')
            for out_edge in out_edges:
                graph.add_edge(f'{node[0]}_out_{edge_pair_id}', out_edge[1])

        elif not out_edges:
            graph.add_node(f'{node[0]}_in_{edge_pair_id}', node_pk=node[0], type='penalty_node')
            for out_edge in out_edges:
                graph.add_edge(f'{node[0]}_out_{edge_pair_id}', out_edge[1])

        for edge_pair in edge_pairs:
            edge_pair_id += 1

            graph.add_node(f'{node[0]}_in_{edge_pair_id}', node_pk=node[0], type='penalty_node')
            graph.add_node(f'{node[0]}_out_{edge_pair_id}', node_pk=node[0], type='penalty_node')

            graph.add_edge(f'{node[0]}_in_{edge_pair_id}', f'{node[0]}_out_{edge_pair_id}',
                           time=1.5, type='penalty_edge')
            graph.add_edge(edge_pair[0][0], f'{node[0]}_{edge_pair_id}_1', **edge_pair[0][2])
            graph.add_edge(f'{node[0]}_{edge_pair_id}_2', edge_pair[1][1], **edge_pair[1][2])
        graph.remove_node(node[0])
        graph.add_node(node[0], **node[1])


def get_shortest_path(graph, source, target):
    for node in graph.nodes(data=True):
        if f'{source}_out' in str(node[0]):
            graph.add_edge(source, node[0], time=0)
        if f'{target}_in' in str(node[0]):
            graph.add_edge(node[0], target, time=0)

    shortest_path = nx.shortest_path(graph, source, target, weight='time')

    return shortest_path


if __name__ == '__main__':
    G = nx.MultiDiGraph()

    node_ids = [1, 2, 3, 4]
    for node in node_ids:
        G.add_node(node, node_pk=node, type='coord')

    G.add_edge(1, 2, time=2)
    G.add_edge(2, 3, time=3)
    G.add_edge(3, 4, time=3)
    G.add_edge(2, 4, time=7)
    # print(G.in_edges(2))
    # print(G.out_edges(2))
    # print(nx.shortest_path(G, 1, 4, weight='time'))
    #
    # print('edges', G.number_of_edges())
    # print('nodes', G.number_of_nodes())
    #
    add_penalties(G)
    print(G.nodes)
    print(get_shortest_path(G, 1, 4))


    # print(nx.shortest_path(G, 1, 4, weight='time'))

    print('edges', G.number_of_edges())
    print('nodes', G.number_of_nodes())
