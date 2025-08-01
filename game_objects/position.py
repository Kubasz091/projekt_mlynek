from utils.validators import TerminalPosition


# y, x
class Position:
    pos: tuple[int, int] = TerminalPosition()  # type: ignore

    def __init__(self, position: tuple[int, int]) -> None:
        self.pos = position

    def __iter__(self):
        return iter(self.pos)

    def __getitem__(self, key: int) -> int:
        return self.pos[key]


if __name__ == "__main__":
    pos = Position((1, 2))

    print(pos[0])  # Output: 1
    print(pos[1])  # Output: 2

    for p in pos:
        print(p)  # Output: 1, then 2
