from data_loaders.class_registry import register_game_object_class
from game_objects.game_object import Connectable, GameObject


@register_game_object_class
class Board(GameObject, Connectable):
    @property
    def player1Pawns(self):
        yield from self.connections["PawnP1"]

    @property
    def player2Pawns(self):
        yield from self.connections["PawnP2"]
