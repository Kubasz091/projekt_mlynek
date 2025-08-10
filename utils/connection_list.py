from collections.abc import Sequence

from utils.position import Position
from utils.unchangable_attribute import CannotChange


#
#
class Connector:
    pos = Position()

    def __init__(self, pos=(0, 0)) -> None:
        self.pos = tuple(pos)
        self.obj = None


class ConnectorList(Sequence):
    _cls = CannotChange()
    _list = CannotChange()

    def __init__(self, cls: type, positions: list[list[int]]) -> None:
        super().__init__()

        self._cls = cls
        self._list = [Connector(pos) for pos in positions]

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
        return self._get_len()

    def __iter__(self):
        return iter(connector.obj for connector in self._list if connector.obj is not None)

    def _get_len(self):
        return sum(connector.obj is not None for connector in self._list)

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


#
#
#
#
#

if __name__ == "__main__":
    from class_registry import register_game_object, resolve_game_object

    _ = register_game_object(int)

    class TestField:
        def __init__(self):
            self.connections = None

        def load(self, data):
            self.connections = {
                name: ConnectorList(resolve_game_object(name), info["positions"])
                for name, info in data["connections"].items()
            }

        def connect(self, obj, pos):
            try:
                self.connections[obj.__class__.__name__].append_at(obj, pos)
            except Exception as e:
                raise ValueError(f"Failed to connect {obj} at {pos}: {e}") from e

    data = {"connections": {"int": [[0, 0], [1, 1], [1, 2]] }}

    test = TestField()
    test.load(data)
    x = 3
    test.connect(3, (1, 2))
