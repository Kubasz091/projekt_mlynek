_CLASS_REGISTRY: dict[str, type] = {}

#


def register_game_object_class(cls: type) -> type:
    _CLASS_REGISTRY[cls.__name__] = cls
    return cls


def resolve_game_object_class(name: str) -> type:
    try:
        return _CLASS_REGISTRY[name]
    except KeyError as e:
        raise ValueError(f"Unknown GameObject name: {name}") from e


def class_registry_dict():
    tmp = []
    for key in _CLASS_REGISTRY.keys():
        tmp.append(key)
    tmp.sort()
    return {"CLASS_REGISTRY": tmp}
