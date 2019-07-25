def get_nodes_by_attr_value(graph, key, value):
    return [(x, y) for x, y in graph.nodes(data=True) if y[f'{key}'] == value]

