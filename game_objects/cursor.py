from data_loaders.terminal_texture import Texture
from game_objects.game_object import GameObject


class Cursor(GameObject):
    def __init__(self, position: tuple[int, int], texture: Texture, bounds: tuple[int, int], id: int):
        super().__init__(id)
        self.position = position
        self.texture = texture
        self.bounds = bounds

    def move(self, new_pos: tuple[int, int]):
        if 0 <= new_pos[0] < self.bounds[0] and 0 <= new_pos[1] < self.bounds[1]:
            self.position = new_pos
