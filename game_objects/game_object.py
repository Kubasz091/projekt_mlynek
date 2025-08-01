from data_loaders.terminal_texture import TerminalTexture
from game_objects.position import Position


class GameObject:
    def __init__(self) -> None:
        self.position = Position((0, 0))
        self.texture = TerminalTexture(["no texture"], [10, 1])
        super().__init__()

    def render(self):
        return self.position.pos, self.texture.texture


if __name__ == "__main__":

    class testClass(GameObject):
        def __init__(self, position: tuple[int, int], texture: list[str]) -> None:
            super().__init__()
            self.texture.texture = texture
            self.position.pos = position

    obj = testClass((1, 2), ["aa", "bbb"])

    print(f"Position: {obj.position}")
    print(f"Texture: {obj.texture}")
