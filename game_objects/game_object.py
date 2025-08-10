import json
from typing import Any

from data_loaders.terminal_texture import Texture
from utils.class_registry import register_game_object, resolve_game_object
from utils.connection_list import ConnectorList
from utils.position import Position
from utils.validators import PositiveInt

#


@register_game_object
class GameObject:
    position: tuple[int, int] = Position()  # type: ignore
    id: int = PositiveInt()  # type: ignore

    def __init__(self, **kwargs) -> None:
        self.position = (0, 0)
        self.id = 0
        self.texture = Texture(["no texture"])

        super().__init__()

        if kwargs:
            self.load(kwargs)

    def load(self, data: dict[str, Any]):
        self.position = tuple(data.get("position", [0, 0]))
        self.id = data.get("id", 0)

        tex = data.get("texture", {})
        self.texture = Texture(tex.get("graphics", ["no texture"]), tex.get("size", None))

        try:
            super().load(data)
        except AttributeError:
            pass

    def render(self):
        return self.position, self.texture.texture, self.texture.size

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
                    "graphics": getattr(self.texture, "texture", None),
                    "size": getattr(self.texture, "size", None),
                },
            }
        )
        ### GAME OBJECT SERIALIZATION ###

        return base

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


@register_game_object
class Connectable:
    def __init__(self, **kwargs) -> None:
        self.connections = {}

        super().__init__()

        if kwargs:
            self.load(kwargs)

    def load(self, data: dict[str, Any]):
        self.connections = {
            name: ConnectorList(resolve_game_object(name), info.get("positions", []))
            for name, info in data.get("connections", {}).items()
        }

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
        for name, positions in self.connections.items():
            connections_data[name] = [list(connector.pos) for connector in positions._list]
        ### CONNECTION SERIALIZATION ###

        base.update({"connections": connections_data})
        return base

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, s: str):
        data = json.loads(s)
        obj = cls(**data)
        return obj


if __name__ == "__main__":
    data = {
        "position": [1, 2],
        "texture": {"graphics": ["aaa", "bbb"], "size": [2, 3]},
        "id": 2,
    }

    obj = GameObject(**data)

    obj2 = GameObject()

    obj2.load(data)

    print(obj.render())
    print(obj.to_json())

    print("---obj2---")

    print(obj2.render())
    print(obj2.to_json())
