import numpy as np

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

        self._cursor_last_direction = (0, 0)
        self._cursor_normal_move = True

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

                    if pawn_caught is not None:
                        if pawn_caught.field is None:
                            pawn_caught.position = cursor.position
                            pawn_caught.disconnect()
                            self._cursor_normal_move = True

                        else:
                            cursor.position = (pawn_caught.field.position[0], pawn_caught.field.position[1])
                            pawn_caught.position = cursor.position
                            self._cursor_normal_move = False
                            self._cursor_last_direction = (0, 0)

                    cursor.pawn = pawn_caught
                    cursor.click()

            else:
                fieldID, _, _ = gor._GAME_OBJECT_HITBOXES["Field"].best_overlap_ids(
                    (cursor.position[0] + cursor.hitbox_position[0], cursor.position[1] + cursor.hitbox_position[1]),
                    np.full_like(cursor.pawn.connector_hitboxes["Field"], 1),
                )

                if fieldID != 0:
                    if not self._cursor_normal_move and fieldID == cursor.pawn.field.id:
                        self._cursor_normal_move = True
                        cursor.pawn.position = cursor.pawn.field.position
                        cursor.pawn = None
                        cursor.click()
                        return

                    field_obj = gor.resolve_game_object("Field", fieldID)

                    if field_obj is not None:
                        cursor.pawn.disconnect()
                        cursor.pawn.connect(field_obj, 1, 1)

                        cursor.pawn.position = field_obj.position
                        cursor.pawn = None
                        cursor.click()
                        gor.reload_hitboxes(cursor._pawn_connection_name)

                elif self._cursor_normal_move is False:
                    cursor.pawn.position = cursor.pawn.field.position
                    cursor.pawn = None
                    cursor.click()
                    self._cursor_normal_move = True

    def cursor_move_function(self, direction, cursor_id):
        cursor = gor.resolve_game_object("Cursor", cursor_id)

        if cursor is not None:
            if cursor.pawn is None or self._cursor_normal_move:
                if direction == "up":
                    cursor.move_up()
                elif direction == "down":
                    cursor.move_down()
                elif direction == "left":
                    cursor.move_left()
                elif direction == "right":
                    cursor.move_right()

            elif cursor.pawn is not None and not self._cursor_normal_move:
                available_field_jumps = cursor.pawn.field.connected_free_fields()

                np_field_jumps = np.array(list(available_field_jumps.keys()))
                max_y = max(0, np.max(np_field_jumps[:, 0]) if len(np_field_jumps) > 0 else 0)
                min_y = min(0, np.min(np_field_jumps[:, 0]) if len(np_field_jumps) > 0 else 0)
                max_x = max(0, np.max(np_field_jumps[:, 1]) if len(np_field_jumps) > 0 else 0)
                min_x = min(0, np.min(np_field_jumps[:, 1]) if len(np_field_jumps) > 0 else 0)

                field_jump = None

                def closest_in_direction():
                    nonlocal available_field_jumps, direction, index
                    start_point = list(self._cursor_last_direction)

                    start_point[index] += direction

                    while -1 <= start_point[index] <= 1:
                        if tuple(start_point) in available_field_jumps:
                            return available_field_jumps[tuple(start_point)], tuple(start_point)
                        start_point[index] += direction

                    return None, None

                if direction == "up" and self._cursor_last_direction[0] < 1 and self._cursor_last_direction[0] < max_y:
                    index = 0
                    direction = 1
                    field_jump, found_pos = closest_in_direction()

                    if field_jump is not None and found_pos is not None:
                        self._cursor_last_direction = found_pos
                    else:
                        self._cursor_last_direction = (self._cursor_last_direction[0] + 1, self._cursor_last_direction[1])
                elif direction == "down" and self._cursor_last_direction[0] > -1 and self._cursor_last_direction[0] > min_y:
                    index = 0
                    direction = -1
                    field_jump, found_pos = closest_in_direction()

                    if field_jump is not None and found_pos is not None:
                        self._cursor_last_direction = found_pos
                    else:
                        self._cursor_last_direction = (self._cursor_last_direction[0] - 1, self._cursor_last_direction[1])
                elif direction == "left" and self._cursor_last_direction[1] > -1 and self._cursor_last_direction[1] > min_x:
                    index = 1
                    direction = -1
                    field_jump, found_pos = closest_in_direction()

                    if field_jump is not None and found_pos is not None:
                        self._cursor_last_direction = found_pos
                    else:
                        self._cursor_last_direction = (self._cursor_last_direction[0], self._cursor_last_direction[1] - 1)
                elif direction == "right" and self._cursor_last_direction[1] < 1 and self._cursor_last_direction[1] < max_x:
                    index = 1
                    direction = 1
                    field_jump, found_pos = closest_in_direction()

                    if field_jump is not None and found_pos is not None:
                        self._cursor_last_direction = found_pos
                    else:
                        self._cursor_last_direction = (self._cursor_last_direction[0], self._cursor_last_direction[1] + 1)

                if field_jump is not None:
                    cursor.position = tuple(field_jump.position)
                elif self._cursor_last_direction == (0, 0):
                    cursor.position = tuple(cursor.pawn.field.position)

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
