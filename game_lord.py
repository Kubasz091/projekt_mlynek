from random import getrandbits
from board import Pawn, Dot
from display import Display


class GameLord:
    def __init__(self, size: int):
        self._dots_list = []
        self._player1_pawns = []
        self._player2_pawns = []
        self._player1_turn = bool(getrandbits(1))

        self._display = Display(size, self)
        self.connect_dots(self._dots_list)

        self._key = None
        self._cursor_x = 0
        self._cursor_y = 0
        self._catch = False
        self._saved_pos = None
        self._position_difference = None
        self._holding_pawn = None
        self._saved_dot = None

    def change_turn(self):
        self._player1_turn = not self._player1_turn

    def add_dot(self, dot: Dot):
        self._dots_list.append(dot)

    def add_player1_pawn(self, pawn: Pawn):
        self._player1_pawns.append(pawn)

    def add_player2_pawn(self, pawn: Pawn):
        self._player2_pawns.append(pawn)

    def check_if_above_pawn(self, position: list):
        pawn_return = None
        for player in [self._player1_pawns, self._player2_pawns]:
            for pawn in player:
                pos_left_corner = pawn.position
                pos_right_corner = [pos_left_corner[0] + len(self._display._graphic_data.graphics_data[f'pawn_player{int(pawn.player_no_1)}'][0]),
                                    pos_left_corner[1] + len(self._display._graphic_data.graphics_data[f'pawn_player{int(pawn.player_no_1)}'])]
                if (position[0] >= pos_left_corner[0] and position[0] < pos_right_corner[0]
                   and position[1] >= pos_left_corner[1] and position[1] < pos_right_corner[1]
                   and pawn.player_no_1 == self._player1_turn):
                    pawn_return = pawn
        return pawn_return

    def check_if_above_dot(self, position: list):
        dot_return = None
        for dot in self._dots_list:
            pos_left_corner = list(dot.position)
            pos_right_corner = [pos_left_corner[0] + len(self._display._graphic_data.graphics_data['dot'][0]),
                                pos_left_corner[1] + len(self._display._graphic_data.graphics_data['dot'])]
            if (position[0] >= pos_left_corner[0] and position[0] < pos_right_corner[0]
               and position[1] >= pos_left_corner[1] and position[1] < pos_right_corner[1]):
                dot_return = dot
        return dot_return

    def connect_dots(self, dots_list: list):
        keys = self._display._graphic_data.board_data["connected_dots"].keys()
        for key in keys:
            for dot in self._display._graphic_data.board_data["connected_dots"][key]:
                dots_list[key].set_connection(dots_list[dot])
                dots_list[dot].set_connection(dots_list[key])

    def keyboard_functionality(self, height: int, width: int):
        if self._key == "KEY_DOWN":
            self._cursor_y = self._cursor_y + 1
        elif self._key == "KEY_UP":
            self._cursor_y = self._cursor_y - 1
        elif self._key == "KEY_RIGHT":
            self._cursor_x = self._cursor_x + 2
        elif self._key == "KEY_LEFT":
            self._cursor_x = self._cursor_x - 2
        elif self._key == 'e':
            self._catch = not self._catch
            if (self._saved_pos is not None and self._holding_pawn is not None):
                dot = self.check_if_above_dot([self._cursor_x, self._cursor_y])
                if (dot is not None and dot.pawn_on_top is None):
                    self._holding_pawn.set_position(dot.position)
                    self._holding_pawn.pawn_was_moved()
                    dot.set_pawn_on_top(self._holding_pawn)
                    if (self._saved_pos != dot.position):
                        self.change_turn()
                else:
                    self._holding_pawn.set_position(self._saved_pos)
                    if (self._saved_dot is not None):
                        self._saved_dot.set_pawn_on_top(self._holding_pawn)

        self._cursor_x = max(0, self._cursor_x)
        self._cursor_x = min(width-2, self._cursor_x)

        self._cursor_y = max(0, self._cursor_y)
        self._cursor_y = min(height-2, self._cursor_y)

        return self._cursor_x, self._cursor_y

    def game_mechanics(self):
        is_blue = True
        if self._catch is True and self._holding_pawn is not None:
            self._holding_pawn.set_position([self._cursor_x-self._position_difference[0], self._cursor_y-self._position_difference[1]])

        if (self._catch is False):
            if self._holding_pawn is not None:
                self._holding_pawn = None
                self._saved_pos = None
                self._position_difference = None
                self._saved_dot = None
        elif (self._catch is True):
            is_blue = False
            if self._holding_pawn is None:
                self._holding_pawn = self.check_if_above_pawn([self._cursor_x, self._cursor_y])
                if self._holding_pawn is None:
                    self._catch = not self._catch
                elif (self._saved_pos is None):
                    self._saved_pos = list(self._holding_pawn.position)
                    self._position_difference = list([self._cursor_x-self._saved_pos[0], self._cursor_y-self._saved_pos[1]])
                    dot = self.check_if_above_dot([self._cursor_x, self._cursor_y])
                    if dot is not None:
                        self._saved_dot = dot
                        dot.set_pawn_on_top(None)
        return is_blue

    def display_frame(self, wrapper):
        self._display.draw_display(wrapper)

    def set_key(self, key):
        self._key = key

    @property
    def key(self):
        return self._key
    @property
    def player1_turn(self):
        return self._player1_turn
