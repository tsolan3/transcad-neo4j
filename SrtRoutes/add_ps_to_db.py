from py2neo import Graph, Node


def get_json_data():
    """
    Получаем данные о трубопроводах из mid файла
    :return:
    """
    with open('SrtRoutesPS.mid', 'r', encoding='cp1251') as f:  # открываем файл с данными
        json_data = []

        # создаем json-объект для всех путей
        for line in f.readlines():
            data = line.split(',')
            json_obj = {
                'pk': int(data[0]),
                'direction': data[2],
                'name': data[3],
                'stop_id': int(data[4]),
                'platform_id': data[5],
                'platform_order': data[6],
                'latitude': data[7],
                'longitude': data[8],
                'passenger_site_id': data[12],
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


def create_ps(graph, json_data):
    for node in json_data:
        graph.create(Node(
            'PHYSICAL_STOP',
            direction=node['direction'],
            name=node['name'],
            stop_id=node['stop_id'],
            platform_id=node['platform_id'],
            platform_order=node['platform_order'],
            passenger_site_id=node['passenger_site_id'],
            longitude=node['longitude'],
            latitude=node['latitude'],
            pk=node['pk'])
        )
    return True


graph1 = connect_graph()
create_ps(graph1, get_json_data())
