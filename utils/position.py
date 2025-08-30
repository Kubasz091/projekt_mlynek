from collections.abc import Sequence

if __name__ == "__main__":
    import sys
    from os.path import abspath, dirname

    sys.path.append(dirname(dirname(abspath(__file__))))

from utils.validators import PositiveInt


class Position2D(Sequence):
    _x = PositiveInt()
    _y = PositiveInt()

    def __init__(self, pos: tuple[int, int] = (0, 0)):
        self._y = pos[0]
        self._x = pos[1]

    #
    # SEQUENCE INTERFACE
    #

    def __iter__(self):
        yield self._y
        yield self._x

    def __getitem__(self, key) -> int:
        match key:
            case 0:
                return self._y
            case 1:
                return self._x
            case _:
                raise ValueError("its a 2D position")

    def __setitem__(self, key, value: int):
        match key:
            case 0:
                self._y = value
            case 1:
                self._x = value
            case _:
                raise ValueError("its a 2D position")

    def __len__(self) -> int:
        return 2

    #
    # VALIDATOR INTERFACE
    #

    def __set_name__(self, cls, name):
        self.name = name

    def __set__(self, instance, value: tuple[int, int]):
        if type(value) is Position2D:
            instance.__dict__[self.name] = value
        else:
            instance.__dict__[self.name] = Position2D(value)

    #

    def __str__(self) -> str:
        return f"({self._y}, {self._x})"

    def __repr__(self) -> str:
        return f"Position2D({self._y}, {self._x})"

    def to_dict(self) -> dict[str, int]:
        return {"y": self._y, "x": self._x}

    @classmethod
    def from_dict(cls, data):
        return cls((data["y"], data["x"]))

    def __eq__(self, value):
        return self[0] == value[0] and self[1] == value[1]


if __name__ == "__main__":
    print("=== Position2D Basic Iteration ===")
    pos = Position2D((0, 1))
    print("Initial pos:", pos)
    print("Iterating over pos:")
    for idx, val in enumerate(pos):
        print(f"  pos[{idx}] -> {val}")

    pos[0] += 1
    print("\nAfter pos[0] += 1 ->", pos)
    print()

    print("=== Descriptor Behavior in TestClass ===")

    class TestClass:
        position = Position2D()

        def __init__(self, pos: tuple[int, int]):
            self.position = pos
            print("  Initialized with position =", self.position)

    test1 = TestClass((3, 5))
    print("Type of test1.position:", type(test1.position))
    test1.position = (6, 7)
    print("After setting tuple (6,7):", test1.position, "| type:", type(test1.position))
    test1.position[0] += 1
    print("After incrementing y by 1:", test1.position)
    print()

    print("=== Shared State Check ===")
    test2 = TestClass((3, 5))
    print("  test2.position:", test2.position)
    test2.position = test1.position
    print(
        "After test2.position = test1.position ->",
        test2.position,
        "test1.position =",
        test1.position,
    )

    test1.position[0] = 1
    test1.position[1] = 2
    print("\nAfter changing test1.position to (1,2):")   # I want it to be able to be referenced that easily for later movement of the pawn with the cursor for example
    print("  test1.position:", test1.position)
    print("  test2.position:", test2.position)
