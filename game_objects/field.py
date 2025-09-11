if __name__ == "__main__":
    import sys
    from os.path import abspath, dirname

    sys.path.append(dirname(dirname(abspath(__file__))))

from data_loaders.class_registry import class_registry_dict, register_game_object_class
from game_objects.game_object import Connectable, GameObject

_direction_map = {
    (1, 5): (0, 1),  # right
    (1, 0): (0, -1),  # left
    (0, 2): (1, 0),  # up
    (2, 2): (-1, 0),  # down
    (2, 5): (-1, 1),  # down-right
    (0, 5): (1, 1),  # up-right
    (2, 0): (-1, -1),  # down-left
    (0, 0): (1, -1),  # up-left
}


@register_game_object_class
class Field(GameObject, Connectable):
    @property
    def edges(self):
        yield from self.connections["Edge"]

    @property
    def pawn(self):
        return self.connections["Pawn"][1]

    def connected_free_fields(self):
        return_dict = {}

        for connector in self.connections["Edge"]._dict.values():
            if connector.obj is not None:
                connector_direction = _direction_map.get((connector.pos.y, connector.pos.x), None)

                next_field = None
                current_edge = connector.obj
                last_connector = connector.connector

                while next_field is None:
                    if len(current_edge.connections["Field"]) > 0:
                        for field_obj_connector in current_edge.connections["Field"]._dict.values():
                            if field_obj_connector is not last_connector:
                                field = field_obj_connector.obj
                                if field is not None and field.id != self.id:
                                    if field.pawn is None:
                                        next_field = field
                                    else:
                                        next_field = -1
                                    break
                    if next_field is not None or next_field == -1 or "Edge" not in current_edge.connections:
                        break

                    for edge_connector in current_edge.connections["Edge"]._dict.values():
                        if edge_connector.id != last_connector.id and edge_connector.obj is not None:
                            last_connector = edge_connector.connector
                            current_edge = edge_connector.obj
                            break

                if next_field is not None and next_field != -1:
                    return_dict[connector_direction] = next_field

        return return_dict


if __name__ == "__main__":
    print(class_registry_dict())
    example_field_data = {
        "id": 1,
        "position": [5, 7],
        "texture": {
            "name": "pawn_player0",
            "size": [3, 6],
        },
        "connections": {
            "Edge": {
                "class_name": "Edge",
                "connector_data": [
                    {"position": [0, 0], "obj": None},
                    {"position": [1, 0], "obj": None},
                    {"position": [0, 1], "obj": None},
                    {"position": [1, 1], "obj": None},
                ],
            },
            "Pawn": {
                "class_name": "Pawn",
                "connector_data": [
                    {"position": [0, 0], "obj": None},
                ],
            },
        },
    }

    test_field = Field()

    print(Field.__mro__)  # turned out as i wanted

    test_field.load(example_field_data)

    print(test_field.render())
    print()

    print("---before connecting---")
    for connect_list in test_field.connections.values():
        for i, item in enumerate(connect_list):
            print(f"{i}. item id: {id(item)}   ", end="")
        print()

    test_field.connect(Pawn(), (0, 0))
    test_field.connect(Edge(), (1, 0))
    test_field.connect(Edge(), (0, 0))

    print("---after connecting---")

    for connect_list in test_field.connections.values():
        for i, item in enumerate(connect_list):
            print(f"{i}. item id: {id(item)}    ", end="")
        print()

    print("---jsonifyiung=---")
    print(test_field.to_json())
