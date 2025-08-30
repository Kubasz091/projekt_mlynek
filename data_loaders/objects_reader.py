import json

from data_loaders.class_registry import resolve_game_object_class
from data_loaders.game_object_registry import (
    _GAME_OBJECT_REGISTRY,
    reasing_put_away_objs_ids,
    register_game_object,
)
from game_objects.game_object import Connectable
from game_objects.game_object import GameObject
from game_objects.edge import Edge
from game_objects.field import Field
from game_objects.pawn import Pawn


if __name__ == "__main__":
    import sys
    from os.path import abspath, dirname

    sys.path.append(dirname(dirname(abspath(__file__))))


_BOARD_SIZE_PATHS = {
    3: "graphic_data/board_size_3.json",
    6: "graphic_data/board_size_6.json",
    9: "graphic_data/board_size_9.json",
    12: "graphic_data/board_size_12.json",
}


def load_game_objects(board_size: int):
    if board_size not in _BOARD_SIZE_PATHS:
        raise ValueError(f"Unsupported board size: {board_size}")

    path = _BOARD_SIZE_PATHS[board_size]

    try:
        with open(path) as file:
            obj_data = json.load(file)

        for class_name, inner_dict in obj_data.items():
            cls = resolve_game_object_class(class_name)
            for _, data in inner_dict.items():
                obj = cls.from_dict(data)
                register_game_object(obj)

        reasing_put_away_objs_ids()

        # connect objects together
        for instance_dict in _GAME_OBJECT_REGISTRY.values():
            for obj in instance_dict.values():
                if isinstance(obj, Connectable):
                    obj.connect_after_load()

    except FileNotFoundError as e:
        raise FileNotFoundError(f"Game object file not found: {path}") from e
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON in game object file: {path}: {e}") from e
    except Exception as e:
        raise RuntimeError(f"Unexpected error loading game object file: {path}: {e}") from e
