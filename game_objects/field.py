from game_objects.game_object import Connectable, GameObject
from utils.class_registry import register_game_object


@register_game_object
class Field(GameObject, Connectable):
    pass


@register_game_object
class Edge:
    pass


@register_game_object
class Pawn:
    pass


if __name__ == "__main__":
    example_field_data = {
        "id": 1,
        "position": [5, 7],
        "texture": {"graphics": ["..", ".."], "size": [2, 2]},
        "connections": {
            "Edge": {"length": 4, "positions": [[0, 0], [1, 0], [0, 1], [1, 1]]},
            "Pawn": {"length": 1, "positions": [[0, 0]]},
        },
    }

    test_field = Field()

    print(Field.__mro__)  # turned out as i wanted

    test_field.load(example_field_data)

    print(test_field.to_json())
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
