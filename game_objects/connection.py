from data_loaders.terminal_texture import TerminalTexture
from game_objects.game_object import GameObject
from game_objects.position import Position
from utils.validators import FixedLengthContainer, TypedList


class Length2FieldList(FixedLengthContainer, TypedList):
    expected_length = 2
    expected_type = (GameObject, type(None))


class Connection(GameObject):
    fields = Length2FieldList()

    def __init__(self, position: Position, texture: TerminalTexture):
        super().__init__()
        self.position = position
        self.texture = texture
        self.fields = [None, None]
