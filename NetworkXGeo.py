import networkx as nx
import time


def get_json_data_nodes():
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


def get_json_data_edges():
    with open('transcad_data/SrtLinks.mid', 'r') as f:
        json_data = []
        line_num = 0
        for line in f.readlines():
            line_num += 1
            data = line.split(',')
            json_obj = {
                'direction': data[2],
                'length': float(data[3]),
                'node_id_from': data[4],
                'node_id_to': data[5],
                'move_time': data[13],
                'line_num': line_num
            }
            json_data.append(json_obj)
    return json_data


def get_coords_data():
    with open('transcad_data/SrtLinks.geo', 'r') as f:
        json_data = []
        line_num = 0
        for line in f.readlines():
            line_num += 1
            data = line.split(',')
            json_obj = {
                'lng1': data[2],
                'lat1': data[3],
                'lng2': data[4],
                'lat2': data[5],
                'line_num': line_num
            }
            json_data.append(json_obj)
    return json_data


def merge_data():
    relations = get_json_data_edges()
    node_coords = get_coords_data()
    merged_relations = []
    for node in node_coords:
        relation = list(filter(lambda rel: rel['line_num'] == node['line_num'], relations))[0]
        relation['lng1'] = float(node['lng1'])
        relation['lng2'] = float(node['lng2'])
        relation['lat1'] = float(node['lat1'])
        relation['lat2'] = float(node['lat2'])
        merged_relations.append(relation)
    return merged_relations


def add_nodes(G, json_data):
    for node in json_data:
        G.add_node(node['pk'], longitude=node['longitude'], latitude=node['latitude'])
    return True


def add_edges(G, json_data):
    for rel in json_data:
        node1 = [x for x, y in G.nodes(data=True) if y['latitude'] == rel['lat1'] and y['longitude'] == rel['lng1']][0]
        print(node1)
        node2 = [x for x, y in G.nodes(data=True) if y['latitude'] == rel['lat2'] and y['longitude'] == rel['lng2']][0]
        if (node1 is not None) and (node2 is not None):
            if int(rel['direction']) == 1:
                G.add_edge(node1, node2, length=rel['length'])
            elif int(rel['direction']) == -1:
                G.add_edge(node2, node1, length=rel['length'])
            else:
                G.add_edge(node1, node2, length=rel['length'])
                G.add_edge(node2, node1, length=rel['length'])
    return True


if __name__ == '__main__':
    G = nx.MultiDiGraph()
    add_nodes(G, get_json_data_nodes())
    add_edges(G, merge_data())

    print(G.number_of_edges())
    print(G.number_of_nodes())
    start_time = time.time()
    print(nx.shortest_path(G, 4805, 4810, weight='length'))
    print("--- %s seconds ---" % (time.time() - start_time))
