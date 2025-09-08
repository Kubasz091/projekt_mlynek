import json

from data_loaders.class_registry import resolve_game_object_class
from data_loaders.game_object_registry import _GAME_OBJECT_REGISTRY, change_board_size, reasing_put_away_objs_ids, register_game_object, reload_hitboxes
from data_loaders.texture_registry import _TERMINAL_GRAPHICS_PATH, TextureRegistry
from game_objects.game_lord import load_gamelord
from game_objects.game_object import Connectable

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
    global _TERMINAL_GRAPHICS_PATH, _BOARD_SIZE_PATHS, _GAME_OBJECT_REGISTRY

    if board_size not in _BOARD_SIZE_PATHS:
        raise ValueError(f"Unsupported board size: {board_size}")

    path = _BOARD_SIZE_PATHS[board_size]

    try:
        with open(path) as file:
            file_data = json.load(file)

        obj_data = file_data.get("objects", None)
        size = file_data.get("display_size", None)
        graphics_used = file_data.get("graphic_data_path", None)

        if size is not None:
            change_board_size((size["y"], size["x"]))

        if graphics_used is not None and graphics_used != _TERMINAL_GRAPHICS_PATH:
            _TERMINAL_GRAPHICS_PATH = graphics_used
            TextureRegistry._instance.clear_data()
            TextureRegistry._instance._load()

        if obj_data is not None:
            for obj_dict in obj_data:
                cls = resolve_game_object_class(obj_dict.get("__type__"))
                obj = cls.from_dict(obj_dict)
                register_game_object(obj)

        reasing_put_away_objs_ids()

        # connect objects together
        for instance_dict in _GAME_OBJECT_REGISTRY.values():
            for obj in instance_dict.values():
                if isinstance(obj, Connectable):
                    obj.connect_after_load()

        mill_map_data = file_data.get("mill_detection_hitbox", None)

        if mill_map_data is not None:
            gl = load_gamelord(mill_map_data)

            print(gl._mill_map)

        reload_hitboxes()

    except FileNotFoundError as e:
        raise FileNotFoundError(f"Game object file not found: {path}") from e
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON in game object file: {path}: {e}") from e
    except Exception as e:
        raise RuntimeError(f"Unexpected error loading game object file: {path}: {e}") from e
