from py2neo import Graph, Relationship, NodeMatcher


def get_json_data():
    """
    Получаем данные о трубопроводах из mid файла
    :return:
    """
    with open('SrtRoutes.mid', 'r') as f:  # открываем файл с данными

        json_data = []

        # создаем json-объект для всех путей
        for line in f.readlines():
            data = line.split(',')
            json_obj = {
                'route_id': int(data[0]),
                'route_name': str(data[1]),
                'car_type': str(data[2]),
                'magistral': data[3],
                'express': data[4],
                'year_start': int(data[5]),
                'year_end': int(data[6]),
                'transport_type': data[7],
                'mode_id': int(data[8]),
                'headway': float(data[9]),
                'headway_midday': data[10],
                'headway_night': data[11],
            }

            # меняем пустые поля на None
            for k, v in json_obj.items():
                if json_obj[k] == '':
                    json_obj[k] = None
                if k in ['magistral', 'express'] and json_obj[k] is not None:
                    json_obj[k] = int(v)  # если значения не None, то делаем их булевыми
                if v == '\n':
                    json_obj[k] = None
                if k in ['headway_midday', 'headway_might'] and json_obj[k] is not None:
                    json_obj[k] = float(v)  # если значения не None, то делаем их float
            json_data.append(json_obj)
    return json_data


def connect_graph():
    graph = Graph("http://localhost:7474/db/data/", user='neo4j', password='119678Qq')
    return graph