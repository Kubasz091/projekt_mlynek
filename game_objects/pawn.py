if __name__ == "__main__":
    import sys
    from os.path import abspath, dirname

    sys.path.append(dirname(dirname(abspath(__file__))))

from data_loaders.class_registry import register_game_object_class
from data_loaders.texture_registry import load_textures
from game_objects.game_object import Connectable, GameObject


@register_game_object_class
class Pawn(GameObject, Connectable):
    pass


@register_game_object_class
class PawnP1(Pawn):
    player_no = 1


@register_game_object_class
class PawnP2(Pawn):
    player_no = 2


if __name__ == "__main__":
    load_textures()

    player1_pawn = PawnP1()
