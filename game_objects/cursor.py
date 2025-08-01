from data_loaders.terminal_texture import TerminalTexture
from game_objects.game_object import GameObject
from game_objects.position import Position


class Cursor(GameObject):
    def __init__(self, position: Position, texture: TerminalTexture, display_size: tuple[int, int]):
        super().__init__()
        self.position = position
        self.texture = texture
        self.display_size = display_size

    def move(self, new_position: Position):
        if (
            0 <= new_position.pos[0] < self.display_size[0]
            and 0 <= new_position.pos[1] < self.display_size[1]
        ):
            self.position = new_position

    def render(self):
        return self.position.pos, self.texture.texture
