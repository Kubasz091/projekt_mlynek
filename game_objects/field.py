if __name__ == "__main__":
    import sys
    from os.path import abspath, dirname

    sys.path.append(dirname(dirname(abspath(__file__))))

from game_objects.game_object import Connectable, GameObject
from utils.class_registry import class_registry_dict, register_game_object_class


@register_game_object_class
class Field(GameObject, Connectable):
    pass



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
