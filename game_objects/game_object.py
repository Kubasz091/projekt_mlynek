import json
from typing import Any

if __name__ == "__main__":
    import sys
    from os.path import abspath, dirname

    sys.path.append(dirname(dirname(abspath(__file__))))

from data_loaders.texture_registry import TextureRegistry
from utils.class_registry import register_game_object_class, resolve_game_object_class
from utils.connection_list import ConnectorList
from utils.game_object_registry import register_game_object
from utils.position import Position2D
from utils.validators import PositiveInt

#


@register_game_object_class
class GameObject:
    position = Position2D()  # type: ignore
    id: int = PositiveInt()  # type: ignore

    def __init__(self, **kwargs) -> None:  # TODO add hints what to add in kwargs
        self.position = (0, 0)
        self.id = 0
        self.texture = TextureRegistry.instance()["no texture"]

        super().__init__()

        if kwargs:
            self.load(kwargs)

        register_game_object(self)

    def load(self, data: dict[str, Any]):
        self.position = data.get("position", (0, 0))
        self.id = data.get("id", 0)

        tex = data.get("texture", None)

        if tex:
            _tex_name = tex.get("name", None)
            _tex_size = tex.get("size", None)

            if _tex_name:
                self.texture = TextureRegistry.instance()[_tex_name]

            if _tex_size and self.texture.size != tuple(_tex_size):
                raise ValueError("error with loaded texture size")

        try:
            super().load(data)
        except AttributeError:
            pass

    def render(self):
        return self.position, list(self.texture), self.texture.size

    #
    ### Json serialization methods ###
    #

    def to_dict(self) -> dict[str, Any]:
        try:
            base = dict(super().to_dict())
        except AttributeError:
            base = {}

        ### GAME OBJECT SERIALIZATION ###
        base.update(
            {
                "__type__": self.__class__.__name__,
                "id": self.id,
                "position": list(self.position),
                "texture": {
                    "name": getattr(self.texture, "name", None),
                    "size": list(getattr(self.texture, "size", None)),
                },
            }
        )
        ### GAME OBJECT SERIALIZATION ###

        return base

    @classmethod
    def from_dict(_, data):
        return resolve_game_object_class(data["__type__"])(**data)

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, s: str):
        data = json.loads(s)
        obj = cls(**data)
        return obj


#
#
#


@register_game_object_class
class Connectable:
    def __init__(self, **kwargs) -> None:
        self.connections = {}

        super().__init__()

        if kwargs:
            self.load(kwargs)

        register_game_object(self)

    def load(self, data: dict[str, Any]):
        self.connections.update(
            {
                name: ConnectorList.from_dict(info)
                for name, info in data.get("connections", {}).items()
            }
        )

        try:
            super().load(data)
        except AttributeError:
            pass

    def connect(self, obj, pos):
        try:
            self.connections[obj.__class__.__name__].append_at(obj, pos)
        except Exception as e:
            raise ValueError(f"Failed to connect {obj} at {pos}: {e}") from e

    #
    ### Json serialization methods ###
    #

    def to_dict(self) -> dict[str, Any]:
        try:
            base = dict(super().to_dict())  # type: ignore
        except AttributeError:
            base = {}

        ### CONNECTION SERIALIZATION ###
        connections_data = {}
        for name, connector_list in self.connections.items():
            connections_data[name] = connector_list.to_dict()
        ### CONNECTION SERIALIZATION ###

        base.update({"connections": connections_data})
        return base

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, s: str):
        data = json.loads(s)
        obj = cls(**data)
        return obj


if __name__ == "__main__":
    data = {
        "__type__": "GameObject",
        "id": 1,
        "position": [12, 3],
        "texture": {
            "name": "pawn_player0",
            "size": [3, 6],
        },
    }

    obj = GameObject.from_dict(data)

    obj2 = GameObject.from_json(json.dumps(data))

    print(obj.render())
    print(obj.to_json())

    print("---obj2---")

    print(obj2.render())
    print(obj2.to_json())
