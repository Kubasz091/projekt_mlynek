import numpy as np

from data_loaders import game_object_registry as gor
from data_loaders.texture_registry import TextureRegistry
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

        self._players_mill_ids = {1: [], 2: []}

        self._cursor_last_direction = (0, 0)
        self._cursor_normal_move = True

        self.current_player = self._random_starting_id()

        self._deletion_moves = 0

        self._past_board_states = np.zeros((0, gor._BOARD_SIZE[0], gor._BOARD_SIZE[1]), dtype=np.uint16)
        self._past_horizon_length = 60
        self._no_of_allowed_repeats = 3

        self._move_queue_index = 0
        self._move_queue = self._create_move_queue()

        self.display = None

        self._mill_map = FullCoverageMap.from_dict(MillMap_data) if MillMap_data else FullCoverageMap()

    def pawn_interact_function(self, cursor_id):  # cursor_id corresponds to player_id
        cursor = gor.resolve_game_object("Cursor", cursor_id)

        if cursor is not None and cursor.id == self.current_player:
            if cursor.pawn is None:
                if self._deletion_moves > 0:  # deletion move
                    other_pawn_name = "PawnP" + str(3 - cursor.id)
                    pawnID, _, _ = gor._GAME_OBJECT_HITBOXES[other_pawn_name].best_overlap_ids(
                        (cursor.position[0] + cursor.hitbox_position[0], cursor.position[1] + cursor.hitbox_position[1]),
                        cursor.hitbox,
                    )

                    if pawnID != 0:
                        pawn_caught = gor.resolve_game_object(other_pawn_name, pawnID)

                        if pawn_caught is not None and pawn_caught.field is not None:
                            pawn_caught.disconnect()

                            gor.un_register_game_object(pawn_caught)
                            gor.reload_hitboxes(other_pawn_name)

                            self._after_move_process(cursor)

                else:  # pickup move
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

            else:  # putdown move
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

                    self._after_move_process(cursor)

                elif self._cursor_normal_move is False:
                    cursor.pawn.position = cursor.pawn.field.position
                    cursor.pawn = None
                    cursor.click()
                    self._cursor_normal_move = True

    def cursor_move_function(self, direction, cursor_id):
        cursor = gor.resolve_game_object("Cursor", cursor_id)

        if cursor is not None and cursor.id == self.current_player:
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

    def _after_move_process(self, cursor):
        deletion_moves_no_granded = self._refresh_mill_ids(cursor)
        self._deletion_moves += deletion_moves_no_granded

        if deletion_moves_no_granded > 0:
            self.display._current_statusbar_text = (
                f"Player {self.current_player} to remove opponent's pawn! ({self._deletion_moves} moves left)"
            )

        if self._deletion_moves > 0 and deletion_moves_no_granded == 0:
            self._deletion_moves -= 1

        if self._deletion_moves == 0:
            self.display._current_statusbar_text = self.display.statusbar_text

            self._append_current_board_state()
            self._next_player()

            if self._check_for_repeated_board_state():
                self._end_game("draw")

            elif len(gor._GAME_OBJECT_REGISTRY["PawnP1"]) < 3:
                self._end_game("player2_won")

            elif len(gor._GAME_OBJECT_REGISTRY["PawnP2"]) < 3:
                self._end_game("player1_won")

    def _append_current_board_state(self):
        current_board_state = gor._GAME_OBJECT_HITBOXES["PawnP1"].hitbox_array.copy()
        current_board_state += gor._GAME_OBJECT_HITBOXES["PawnP2"].hitbox_array * 2

        self._past_board_states = np.concatenate((self._past_board_states, current_board_state[np.newaxis, :, :]), axis=0)

    def _check_for_repeated_board_state(self):
        current_board_state = self._past_board_states[-1]

        if len(self._past_board_states) > self._past_horizon_length:
            return (
                np.sum(np.all(self._past_board_states[: -self._past_horizon_length] == current_board_state, axis=(1, 2)))
                >= self._no_of_allowed_repeats
            )
        else:
            return np.sum(np.all(self._past_board_states[:-1] == current_board_state, axis=(1, 2))) >= self._no_of_allowed_repeats

    def _refresh_mill_ids(self, cursor):
        grand_deletion_moves = 0
        if cursor.id in self._players_mill_ids:
            completed_mills, count = self._mill_map.fully_covered_ids(gor._GAME_OBJECT_HITBOXES[cursor._pawn_connection_name])

            grand_deletion_moves = max(0, count - len(self._players_mill_ids[cursor.id]))

            self._players_mill_ids[cursor.id] = completed_mills

        return grand_deletion_moves

    def _random_starting_id(self):
        return np.random.choice(self._human_players + self._bot_players)

    def _create_move_queue(self):
        _move_queue = self._human_players + self._bot_players
        np.random.shuffle(_move_queue)
        self._move_queue_index = _move_queue.index(self.current_player)
        return _move_queue

    def _next_player(self):
        self._move_queue_index = (self._move_queue_index + 1) % len(self._move_queue)
        self.current_player = self._move_queue[self._move_queue_index]

    def _end_game(self, end):
        texture = None
        if end in ["draw", "player1_won", "player2_won"]:
            _reg = TextureRegistry.instance()
            texture = _reg[end]

        if texture:
            import time

            self.display.output.clear()
            self.display.draw_texture(lambda: ((5, 10), texture))
            self.display.output.refresh()
            time.sleep(3)

        self.display.running = False


def load_gamelord(MillMap_data):
    return GameLord(MillMap_data)
