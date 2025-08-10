from copy import copy

from utils.validators import RectangularStringList


class Texture:
    texture: list[str] = RectangularStringList()  # type: ignore

    def __init__(self, texture: list[str], size: tuple[int, int] | None = None) -> None:
        self.texture = texture

        # (y, x)
        if size is None:
            self._size = (len(texture), len(texture[0]))
        else:
            self._size = copy(size)
            if len(texture) != self._size[0] or len(texture[0]) != self._size[1]:  # type: ignore
                raise ValueError("Texture dimensions do not match the specified size.")

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
    tex = Texture(["aaaa", "bbbb", "cccc"], (3, 4))

    print(tex.size)
