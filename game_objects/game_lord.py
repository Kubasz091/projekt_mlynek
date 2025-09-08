from data_loaders import game_object_registry as gor
from game_objects.hitboxes import FullCoverageMap


# SINGLETON
class GameLord:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, MillMap_data=None):
        self._mill_map = FullCoverageMap.from_dict(MillMap_data) if MillMap_data else FullCoverageMap()

    def catch_check(self, cursor1, input_passer):
        caught = False
        pawn_caught = None

        def do_check():
            nonlocal caught, pawn_caught

            curr_key = input_passer()
            if curr_key == ord("e") and not caught:
                pawnID, _, _ = gor._GAME_OBJECT_HITBOXES["PawnP2"].best_overlap_ids(
                    (cursor1.position[0] + cursor1.hitbox_position[0], cursor1.position[1] + cursor1.hitbox_position[1]),
                    cursor1.connector_hitboxes["PawnP2"].hitbox_array,
                )
                if pawnID != 0:
                    pawn_caught = gor.resolve_game_object("PawnP2", pawnID)
                    pawn_caught.position = cursor1.position
                    caught = True

            elif curr_key == ord("e") and caught and pawn_caught is not None:
                fieldID, _, _ = gor._GAME_OBJECT_HITBOXES["Field"].best_overlap_ids(
                    (cursor1.position[0] + cursor1.hitbox_position[0], cursor1.position[1] + cursor1.hitbox_position[1]),
                    cursor1.connector_hitboxes["PawnP2"].hitbox_array,
                )
                if fieldID != 0:
                    field_obj = gor.resolve_game_object("Field", fieldID)
                    pawn_caught.position = field_obj.position
                    caught = False
                    pawn_caught = None

        return do_check


def load_gamelord(MillMap_data):
    return GameLord(MillMap_data)
