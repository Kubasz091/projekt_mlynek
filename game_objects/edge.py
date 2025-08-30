if __name__ == "__main__":
    import sys
    from os.path import abspath, dirname

    sys.path.append(dirname(dirname(abspath(__file__))))

from data_loaders.class_registry import register_game_object_class
from game_objects.game_object import Connectable, GameObject


@register_game_object_class
class Edge(GameObject, Connectable):
    pass


if __name__ == "__main__":
    e1 = Edge()
    print(isinstance(e1, Connectable))
