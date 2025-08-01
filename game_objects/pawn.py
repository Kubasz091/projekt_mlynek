from data_loaders.terminal_texture import TerminalTexture
from game_objects.game_object import GameObject
from game_objects.position import Position


class Pawn(GameObject):
    def __init__(self, position: Position, texture: TerminalTexture):
        super().__init__()
        self.position = position
        self.texture = texture
