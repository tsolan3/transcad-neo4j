from pprint import pprint


def get_json_data():
    """
    Получаем данные о трубопроводах из mid файла
    :return:
    """
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
                'is_tram': data[7],
                'is_bus': data[8],
                'is_trolleybus': data[9],
                'is_connector': data[10],
                'link_type_id': int(data[11]),
                'pedestrian_mode_id': int(data[12]),
                'move_time': data[13],
                'walking_time': data[14],
                'null_time': data[15],
                'time_bus': data[16],
                'time_tram': data[17],
                'line_num': line_num
            }
            # меняем пустые поля на None
            for k, v in json_obj.items():
                if json_obj[k] == '':
                    json_obj[k] = None
                if k in ['is_tram', 'is_bus', 'is_trolleybus', 'is_connector'] and json_obj[k] is not None:
                    json_obj[k] = bool(int(v))
                if v == '\n':
                    json_obj[k] = None
                if k in ['walking_time', 'null_time', 'time_bus', 'time_tram'] and json_obj[k] is not None:
                    json_obj[k] = float(v)

            if json_obj['link_type_id'] == 1026:
                json_obj['speed'] = 18
            if json_obj['link_type_id'] == 1032 or 1034:
                json_obj['speed'] = 21
            if json_obj['link_type_id'] == 2048:
                json_obj['speed'] = 3
            json_data.append(json_obj)
    return json_data

data = get_json_data()
pprint(len(data))
print(len([x['speed'] for x in data ]))
from py2neo import Graph, Relationship, NodeMatcher


def get_json_data():
    """
    Получаем данные о трубопроводах из mid файла
    :return:
    """
    with open('transcad_data/SrtLinks.mid', 'r') as f:  # открываем файл с данными

        json_data = []
        line_num = 0  # добавляю нумерацию, чтобы позже синхронизовать с данными о координатах начала и конца

        # создаем json-объект для всех путей
        for line in f.readlines():
            line_num += 1
            data = line.split(',')
            json_obj = {
                'direction': data[2],
                'length': float(data[3]),
                'node_id_from': data[4],
                'node_id_to': data[5],
                'is_tram': data[7],
                'is_bus': data[8],
                'is_trolleybus': data[9],
                'is_connector': data[10],
                'link_type_id': int(data[11]),
                'pedestrian_mode_id': int(data[12]),
                'move_time': data[13],
                'walking_time': data[14],
                'null_time': data[15],
                'time_bus': data[16],
                'time_tram': data[17],
                'line_num': line_num
            }

            # меняем пустые поля на None
            for k, v in json_obj.items():
                if json_obj[k] == '':
                    json_obj[k] = None
                if k in ['is_tram', 'is_bus', 'is_trolleybus', 'is_connector'] and json_obj[k] is not None:
                    json_obj[k] = bool(int(v))  # если значения не None, то делаем их булевыми
                if v == '\n':
                    json_obj[k] = None
                if k in ['walking_time', 'null_time', 'time_bus', 'time_tram'] and json_obj[k] is not None:
                    json_obj[k] = float(v)  # если значения не None, то делаем их float

            # добавляем значения скорости к каждому пути
            if json_obj['link_type_id'] == 1026:
                json_obj['speed'] = 18
            if json_obj['link_type_id'] == 1032 or 1034:
                json_obj['speed'] = 21
            if json_obj['link_type_id'] == 2048:
                json_obj['speed'] = 3
            json_data.append(json_obj)
    return json_data


def get_coords_data():
    """
    Получаем данные о координатах точек путей из geo файла
    :return:
    """
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
    """
    для каждого пути добавляем координаты точек начала и конца
    :return:
    """
    relations = get_json_data()
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


def connect_graph():
    graph = Graph("http://localhost:7474/db/data/", user='neo4j', password='119678Qq')
    return graph


def create_relationships(graph, json_data):
    """
    создаем пути в бд
    :param graph:
    :param json_data:
    :return:
    """
    graph = connect_graph()
    matcher = NodeMatcher(graph)
    for rel in json_data:
        node1 = matcher.match('COORDINATE', latitude=rel['lat1'], longitude=rel['lng1']).first()
        node2 = matcher.match('COORDINATE', latitude=rel['lat2'], longitude=rel['lng2']).first()
        if (node1 is not None) and (node2 is not None):
            if int(rel['direction']) == 1:
                relation = Relationship(
                    node1, 'PATH', node2,
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
                    time_tram=rel['time_tram']
                )
                graph.create(relation)

            elif int(rel['direction']) == -1:
                relation = Relationship(
                    node2, 'PATH', node1,
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
                    time_tram=rel['time_tram']
                )
                graph.create(relation)

            else:
                relation1 = Relationship(
                    node1, 'PATH', node2,
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
                    time_tram=rel['time_tram']
                )
                relation2 = Relationship(
                    node2, 'PATH', node2,
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
                    time_tram=rel['time_tram']
                )
                graph.create(relation1)
                graph.create(relation2)
    return True

graph1 = connect_graph()
data = merge_data()
print('data merged')
create_relationships(graph1, data)
