from data_loaders.terminal_texture import TerminalTexture
from game_objects.game_object import GameObject
from game_objects.position import Position
from utils.validators import FixedLengthContainer, Typed, TypedList


class Length8ConnectionList(FixedLengthContainer, TypedList):
    expected_length = 8
    expected_type = (GameObject, type(None))


class PawnConnection(Typed):
    expected_type = (GameObject, type(None))


class Field(GameObject):
    connections = Length8ConnectionList()
    pawn = PawnConnection()

    def __init__(self, position: Position, texture: TerminalTexture):
        super().__init__()
        self.position = position
        self.texture = texture
        self.connections = [None] * 8
        self.pawn = None
