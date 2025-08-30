from collections.abc import Sequence

if __name__ == "__main__":
    import sys
    from os.path import abspath, dirname

    sys.path.append(dirname(dirname(abspath(__file__))))

from data_loaders.class_registry import resolve_game_object_class
from data_loaders.game_object_registry import resolve_game_object
from utils.position import Position2D
from utils.unchangable_attribute import CannotChange

#
#


class Connector:
    pos = Position2D()

    def __init__(self, **kwargs) -> None:
        self.pos = (0, 0)
        self.obj = None
        self.obj_dict = None

        if kwargs:
            pos_data = kwargs.get("position", None)
            if pos_data:
                self.pos = Position2D.from_dict(pos_data)

            self.obj_dict = kwargs.get(
                "obj", None
            )  # save for later to connect after loading all the objects

    #
    # JSON
    #

    def to_dict(self):
        temp = {"position": self.pos.to_dict(), "obj": None}
        if self.obj:
            temp["obj"] = {"id": self.obj.id, "class_name": self.obj.__class__.__name__}
        return temp

    def connect_from_previous_load(self):
        if self.obj_dict:
            try:
                self.obj = resolve_game_object(
                    self.obj_dict.get("class_name", None), self.obj_dict.get("id", None)
                )
            except Exception as e:
                print(f"failed to locate object assigned to the connector with exception: {e}")

        try:
            delattr(self, "obj_dict")
        except AttributeError:
            pass

    @classmethod
    def from_dict(cls, data):
        return cls(**data)


#


class ConnectorList(Sequence):
    _cls = CannotChange()
    _list = CannotChange()

    def __init__(
        self, cls: type, data: list[dict[str, list[int] | dict[str, int | str]]] | None = None
    ) -> None:
        super().__init__()

        self._cls = cls
        self._list = [Connector.from_dict(item) for item in data]

    #
    # SEQUENCE INTERFACE
    #

    def __setitem__(self, key, value):
        if value is None:
            self._list[key].obj = None
        else:
            raise ValueError(
                f"Cannot set item at index {key}. Use append() or preferably append_at() instead."
            )

    def __getitem__(self, key):
        return self._list[key].obj

    def __len__(self):
        return sum(connector.obj is not None for connector in self._list)

    def __iter__(self):
        return iter(connector.obj for connector in self._list if connector.obj is not None)

    #
    #
    #

    def append(self, obj):
        if obj.__class__ is not self._cls:
            raise ValueError(
                f"Object must be of type {self._cls.__name__}, got {obj.__class__.__name__}"
            )

        for connector in self._list:
            if connector.obj is None:
                connector.obj = obj
                return connector.pos

        raise ValueError("no room")

    def append_at(self, obj, pos):
        if obj.__class__ is not self._cls:
            raise ValueError(
                f"Object must be of type {self._cls.__name__}, got {obj.__class__.__name__}"
            )

        for connector in self._list:
            if connector.pos == pos and connector.obj is None:
                connector.obj = obj
                return pos

        raise ValueError(f"No connections available at position {pos}")

    def connect_from_previous_load(self):
        for connector in self._list:
            connector.connect_from_previous_load()

    #
    # JSON
    #
    def to_dict(self) -> dict[str, list[list[int]]]:
        return {
            "class_name": self._cls.__name__,
            "connector_data": [connector.to_dict() for connector in self._list],
        }

    @classmethod
    def from_dict(cls, data):
        return cls(resolve_game_object_class(data["class_name"]), data["connector_data"])


#
#
#
#
#

if __name__ == "__main__":
    from data_loaders.class_registry import register_game_object_class, resolve_game_object_class
    from data_loaders.game_object_registry import register_game_object, resolve_game_object

    _ = register_game_object_class(int)

    class TestConnectable:
        def __init__(self, **kwargs):
            self.connections = {}

            if kwargs:
                self.load(kwargs)

        def load(self, data):
            self.connections.update(
                {name: ConnectorList.from_dict(info) for name, info in data.items()}
            )

        def connect(self, obj, pos):
            try:
                self.connections[obj.__class__.__name__].append_at(obj, pos)
            except Exception as e:
                raise ValueError(f"Failed to connect {obj} at {pos}: {e}") from e

    data = {
        "int": {
            "class_name": "int",
            "connector_data": [
                {"position": {"y": 0, "x": 0}, "obj": {"id": 1, "class_name": "int"}},
                {"position": {"y": 0, "x": 1}, "obj": {"id": 2, "class_name": "int"}},
                {"position": {"y": 0, "x": 2}, "obj": None},
            ],
        },
    }

    x = 3

    y = 4

    register_game_object(x)
    register_game_object(y)

    test = TestConnectable(**data)

    z = 5
    test.connect(z, (0, 2))

    w = 6

    try:
        test.connect(w, (1, 0))
    except Exception as e:
        print(e)
