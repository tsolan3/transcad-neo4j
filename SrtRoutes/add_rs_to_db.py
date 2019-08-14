from py2neo import Graph, Node


def get_json_data():
    """
    Получаем данные о трубопроводах из mid файла
    :return:
    """
    with open('SrtRoutesRS.mid', 'r', encoding='cp1251') as f:  # открываем файл с данными
        json_data = []

        # создаем json-объект для всех путей
        for line in f.readlines():
            data = line.split(',')
            json_obj = {
                'pk': int(data[0]),
                'route_id': data[2],
                'pass_count': data[3],
                'milepost': float(data[4]),
                'physical_stop_id': data[5],
                'stop_id': data[6],
                'node_id': data[7],
            }

            # меняем пустые поля на None
            for k, v in json_obj.items():
                if json_obj[k] == '':
                    json_obj[k] = None
                if v == '\n':
                    json_obj[k] = None
            json_data.append(json_obj)

    return json_data


def connect_graph():
    graph = Graph("http://localhost:7474/db/data/", user='neo4j', password='119678Qq')
    return graph


def create_rs(graph, json_data):
    for node in json_data:
        graph.create(Node(
            'ROUTE_STOP',
            route_id=node['route_id'],
            pass_count=node['pass_count'],
            milepost=node['milepost'],
            physical_stop_id=node['physical_stop_id'],
            stop_id=node['stop_id'],
            node_id=node['node_id'],
            pk=node['pk'])
        )
    return True


graph1 = connect_graph()
create_rs(graph1, get_json_data())
