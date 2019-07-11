from py2neo import Graph, Node


def get_json_data():
    with open('transcad_data/SrtLinks.geo', 'r') as f:
        json_data = []
        for line in f.readlines():
            data = line.split(',')
            json_obj = {'longitude': float(data[2]), 'latitude': float(data[3])}
            json_data.append(json_obj)
            json_obj = {'longitude': float(data[4]), 'latitude': float(data[5])}
            json_data.append(json_obj)
    distinct_data = [dict(t) for t in {tuple(d.items()) for d in json_data}]
    pk = 0
    for obj in distinct_data:
        pk += 1
        obj['pk'] = pk
    return distinct_data


def connect_graph():
    graph = Graph("http://localhost:7474/db/data/", user='neo4j', password='119678Qq')
    return graph


def create_nodes(graph, json_data):
    nodes = []
    for node in json_data:
        graph.create(Node('COORDINATE', longitude=node['longitude'], latitude=node['latitude'], pk=node['pk']))
    # graph.create(*nodes)
    return True


graph1 = connect_graph()
create_nodes(graph1, get_json_data())
