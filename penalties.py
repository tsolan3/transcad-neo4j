import itertools

from neo4j_to_networkx import get_penalties_data


def add_penalty_edges(graph):
    penalties = get_penalties_data()  # данные о штрафах из файла
    coordinate_nodes = list(graph.nodes)[:]  # получаем все координатные узлы и делаем копию на всякий случай
    for node in coordinate_nodes:
        in_edges = graph.in_edges(node, data=True)  # для каждой координатной точки ищем входящие и выходящие ребра
        out_edges = graph.out_edges(node, data=True)
        edge_pairs = list(itertools.product(in_edges, out_edges))  # находим пары ребер
        for edge_pair in edge_pairs:
            in_edge_link_type = edge_pair[0][2]['link_type_id']
            out_edge_link_type = edge_pair[1][2]['link_type_id']
            for data in penalties:
                if [in_edge_link_type, out_edge_link_type] == [data['link_type_id_1'], data['link_type_id_2']]:
                        # and data['normal_penalty'] != 0:
                    graph.add_edge(node, node, time=data['normal_penalty'], type='penalty')