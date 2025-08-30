import json
from typing import Any

if __name__ == "__main__":
    import sys
    from os.path import abspath, dirname

    sys.path.append(dirname(dirname(abspath(__file__))))

from data_loaders.class_registry import register_game_object_class
from data_loaders.texture_registry import TextureRegistry
from utils.connection_list import ConnectorList
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

    def load(self, data: dict[str, Any]):
        pos_data = data.get("position", None)
        if pos_data:
            self.position = Position2D.from_dict(pos_data)

        self.id = data.get("id", 0)

        tex = data.get("texture", None)

        if tex:
            self.texture = TextureRegistry.from_dict(tex)

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
                "position": self.position.to_dict(),
                "texture": self.texture.to_dict(),
            }
        )
        ### GAME OBJECT SERIALIZATION ###

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

    def load(self, data: dict[str, Any]):
        self.connections.update(
            {
                class_name: ConnectorList.from_dict(info)
                for class_name, info in data.get("connections", {}).items()
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

    def connect_after_load(self):
        for connector_list in self.connections.values():
            connector_list.connect_from_previous_load()

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
        "position": {"y": 12, "x": 3},
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
