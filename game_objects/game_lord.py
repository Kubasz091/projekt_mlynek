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
        self._human_players = [1, 2]
        self._bot_players = []
        self._mill_map = FullCoverageMap.from_dict(MillMap_data) if MillMap_data else FullCoverageMap()

    def pawn_interact_function(self, cursor_id):  # cursor_id corresponds to player_id
        cursor = gor.resolve_game_object("Cursor", cursor_id)

        if cursor is not None:
            if cursor.pawn is None:
                pawnID, _, _ = gor._GAME_OBJECT_HITBOXES[cursor._pawn_connection_name].best_overlap_ids(
                    (cursor.position[0] + cursor.hitbox_position[0], cursor.position[1] + cursor.hitbox_position[1]),
                    cursor.hitbox,
                )

                if pawnID != 0:
                    pawn_caught = gor.resolve_game_object(cursor._pawn_connection_name, pawnID)
                    pawn_caught.position = cursor.position
                    cursor.pawn = pawn_caught

                    pawn_caught.disconnect()
                    cursor.click()

            else:
                fieldID, _, _ = gor._GAME_OBJECT_HITBOXES["Field"].best_overlap_ids(
                    (cursor.position[0] + cursor.hitbox_position[0], cursor.position[1] + cursor.hitbox_position[1]),
                    cursor.pawn.connector_hitboxes["Field"],
                )

                if fieldID != 0:
                    field_obj = gor.resolve_game_object("Field", fieldID)

                    try:
                        cursor.pawn.try_connect("Field")
                    except ValueError:
                        pass

                    if cursor.pawn.field is not None:
                        cursor.pawn.position = field_obj.position
                        cursor.pawn = None
                        cursor.click()
                        gor.reload_hitboxes(cursor._pawn_connection_name)

    def cursor_move_function(self, direction, cursor_id):
        cursor = gor.resolve_game_object("Cursor", cursor_id)

        if cursor is not None:
            if direction == "up":
                cursor.move_up()
            elif direction == "down":
                cursor.move_down()
            elif direction == "left":
                cursor.move_left()
            elif direction == "right":
                cursor.move_right()

    def quit_function(self, display):
        def quit_pass_function(cursor_id):
            if cursor_id in self._human_players:
                display.running = False

        return quit_pass_function

    def switch_player_access(self, player_id):
        if player_id in self._human_players:
            self._human_players.remove(player_id)
            self._bot_players.append(player_id)
        elif player_id in self._bot_players:
            self._bot_players.remove(player_id)
            self._human_players.append(player_id)


def load_gamelord(MillMap_data):
    return GameLord(MillMap_data)
