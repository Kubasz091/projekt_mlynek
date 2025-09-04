from data_loaders.class_registry import register_game_object_class
from data_loaders.game_object_registry import _GAME_OBJECT_REGISTRY
from game_objects.game_object import Connectable, GameObject


@register_game_object_class
class Board(GameObject, Connectable):
    def __init__(self, size: tuple, **kwargs):
        super().__init__(**kwargs)
        self.size = size
        self.game_objects = _GAME_OBJECT_REGISTRY

    @property
    def player1Pawns(self):
        yield from self.connections["PawnP1"]

    @property
    def player2Pawns(self):
        yield from self.connections["PawnP2"]
