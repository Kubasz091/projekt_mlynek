from collections.abc import Sequence
from copy import copy

if __name__ == "__main__":
    import sys
    from os.path import abspath, dirname

    sys.path.append(dirname(dirname(abspath(__file__))))

from utils.validators import NonEmpty, RectangularStringTuple


class Texture(Sequence):
    _texture = RectangularStringTuple()
    _name = NonEmpty()

    def __init__(self, name: str, texture: list[str], size: tuple[int, int] | None = None) -> None:
        self._name = name
        self._change_texture(texture, size)

    #
    # SEQUENCE INTERFACE
    #

    def __iter__(self):
        return iter(self._texture)

    def __getitem__(self, key) -> str:
        return self._texture[key]

    def __setitem__(self, key, value):
        self._texture[key] = value  # will raise Error but allowing on purpose

    def __len__(self) -> int:
        return len(self._texture)

    #
    #
    #

    def _change_texture(self, texture, size=None):
        self._texture = tuple(copy(row) for row in texture)

        # (y, x)
        if size is None:
            self._size = (len(self._texture), len(self._texture[0]))
        else:
            self._size = size  # no copy since tuple is immutable, can't delete through reference
            if len(self._texture) != self._size[0] or len(self._texture[0]) != self._size[1]:  # type: ignore
                raise ValueError("Texture dimensions do not match the specified size.")

    @property
    def size(self) -> tuple[int, int]:
        return self._size

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value


#
#
#
#
#


if __name__ == "__main__":
    tex = Texture("test", ["aaaa", "bbbb", "cccc"], (3, 4))

    print(tex.size)

    #

    print("\n1 -----")
    try:
        tex[0] = "bb"
    except Exception as e:
        print("ERROR:", e)

    #

    print("\n2 -----")
    try:
        tex._change_texture("bb")
    except Exception as e:
        print("ERROR:", e)
    print(list(tex))

    #

    print("\n3 -----")
    try:
        tex._change_texture(["bb", "a"])
    except Exception as e:
        print("ERROR:", e)
    print(list(tex))

    #

    print("\n4 -----")
    try:
        tex._change_texture("ccc", [1, 4])
    except Exception as e:
        print("ERROR:", e)
    print(list(tex))
    print(tex.size)
