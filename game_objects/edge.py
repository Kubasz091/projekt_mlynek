from data_loaders.terminal_texture import Texture
from game_objects.game_object import GameObject
from utils.position import Position
from utils.validators import FixedLengthContainer, TypedList


class Length2FieldList(FixedLengthContainer, TypedList):
    expected_length = 2
    expected_type = (GameObject, type(None))


class Edge(GameObject):  # TODO rename to edge
    fields = Length2FieldList()

    def __init__(self, position: Position, texture: Texture):
        super().__init__()
        self.position = position
        self.texture = texture
        self.fields = [None, None]
