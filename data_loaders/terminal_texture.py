from utils.validators import RectangularStringList


class TerminalTexture:
    texture: list[str] = RectangularStringList()  # type: ignore

    def __init__(self, texture: list[str], size: list[int]) -> None:
        self.texture = texture
        self._size = (size[0], size[1])

    def __iter__(self):
        return iter(self.texture)

    def __getitem__(self, key) -> str:
        return self.texture[key]

    def __len__(self) -> int:
        return len(self.texture)

    @property
    def size(self) -> tuple[int, int]:
        return self._size


if __name__ == "__main__":
    tex = TerminalTexture(["aaaa", "bbbb", "cccc"], [4, 3])

    print(tex.size)
