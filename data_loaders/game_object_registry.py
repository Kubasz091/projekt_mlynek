import numpy as np

_GAME_OBJECT_REGISTRY: dict[str, dict[int, object]] = {}  # dict[class_name][id] = object
_objs_put_away_to_reassing_id: dict[str, list[object]] = {}  # FIFO

#


def register_game_object(game_object):
    _cls_name = game_object.__class__.__name__

    if _cls_name not in _GAME_OBJECT_REGISTRY:
        _GAME_OBJECT_REGISTRY[_cls_name] = {}

    if (
        hasattr(game_object, "id") is False
        or game_object.id == 0
        or game_object.id is None
        or game_object.id in _GAME_OBJECT_REGISTRY[_cls_name]
    ):
        if _cls_name not in _objs_put_away_to_reassing_id:
            _objs_put_away_to_reassing_id[_cls_name] = [game_object]
        else:
            _objs_put_away_to_reassing_id[_cls_name].append(game_object)
        return

    else:
        _GAME_OBJECT_REGISTRY[_cls_name][game_object.id] = game_object


def reasing_put_away_objs_ids():
    for class_name, obj_list in _objs_put_away_to_reassing_id.items():
        total_length = len(_GAME_OBJECT_REGISTRY[class_name]) + len(obj_list)

        free_ids = np.arange(1, total_length + 1, 1, dtype="uint16")
        _existing_ids = np.array(list(_GAME_OBJECT_REGISTRY[class_name].keys()), dtype="uint16")

        free_ids = free_ids[~np.isin(free_ids, _existing_ids)]

        for new_id, obj in zip(free_ids, obj_list):
            new_id = int(new_id)

            try:
                obj.id = new_id
            except AttributeError:
                pass

            _GAME_OBJECT_REGISTRY[class_name][new_id] = obj


def resolve_game_object(class_name: str, id: int):
    try:
        return _GAME_OBJECT_REGISTRY[class_name][id]
    except KeyError as e:
        raise ValueError(f"Unknown GameObject: {class_name} with id: {id}") from e


def game_object_registry_ids_dict():
    tmp = {}
    for class_name, inner_dict in _GAME_OBJECT_REGISTRY.items():
        tmp[class_name] = []
        for id, _ in inner_dict.items():
            tmp[class_name].append(id)
    return {"GAME_OBJECT_REGISTRY": tmp}


def game_objects_to_dict():
    tmp = {}
    for class_name, inner_dict in _GAME_OBJECT_REGISTRY.items():
        tmp[class_name] = {}
        for id, obj in inner_dict.items():
            try:
                tmp[class_name][id] = obj.to_dict()
            except Exception as e:
                raise RuntimeError(
                    f"Failed to serialize {obj} of class {class_name} with id {id}: {e}"
                ) from e
    return tmp


def all_game_objects_generator():
    for inner_dict in _GAME_OBJECT_REGISTRY.values():
        yield from inner_dict.values()
