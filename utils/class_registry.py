from __future__ import annotations

#

_CLASS_REGISTRY: dict[str, type] = {}

#


def register_game_object(cls: type) -> type:
    _CLASS_REGISTRY[cls.__name__] = cls
    return cls


def resolve_game_object(name: str) -> type:
    try:
        return _CLASS_REGISTRY[name]
    except KeyError as e:
        raise ValueError(f"Unknown GameObject name: {name}") from e
