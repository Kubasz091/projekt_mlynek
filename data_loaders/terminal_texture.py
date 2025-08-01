from utils.validators import RectangularStringList

class TerminalTexture():
    texture: list[str] = RectangularStringList() # type: ignore

    def __init__(self, texture: list[str]) -> None:
        self.texture = texture

    def __iter__(self):
        return iter(self.texture)

    def __getitem__(self, key) -> str:
        return self.texture[key]

    def __len__(self) -> int:
        return len(self.texture)

    @property
    def size(self) -> tuple[int, int]:
        return (len(self.texture), len(self.texture[0]))


if __name__ == "__main__":
    tex = TerminalTexture(['aaaa', 'bbbb', 'cccc'])

    print(tex.size)