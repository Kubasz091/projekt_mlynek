from random import getrandbits
from board import Pawn, Dot
from display import Display


class GameLord:
    def __init__(self, size: int):
        self._dots_list = []
        self._player1_pawns = []
        self._player2_pawns = []
        self._active_mills = []
        self._player1_turn = bool(getrandbits(1))
        self._render_one_more_frame = False

        self._display = Display(size, self)
        self.connect_dots(self._dots_list)

        self._cursor_x = 0
        self._cursor_y = 0

        self._catch = False
        self._deletion_move = False
        self._end_game = False

        self._key = None
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
                   and position[1] >= pos_left_corner[1] and position[1] < pos_right_corner[1]):
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

    def check_move(self, dot: Dot):
        if (self._holding_pawn.player_no_1 is True):
            if (dot in self._saved_dot.connected_dots or len(self._player1_pawns) < 4):
                return True
            else:
                return False
        elif (self._holding_pawn.player_no_1 is False):
            if (dot in self._saved_dot.connected_dots or len(self._player2_pawns) < 4):
                return True
            else:
                return False

    def check_mills(self):
        player1_pawns_on_board = []
        player2_pawns_on_board = []

        for pawn in self._player1_pawns:
            if pawn.has_been_moved is True and pawn is not self._holding_pawn:
                player1_pawns_on_board.append(pawn)
        for pawn in self._player2_pawns:
            if pawn.has_been_moved is True and pawn is not self._holding_pawn:
                player2_pawns_on_board.append(pawn)

        found_mills = self.search_mills(player1_pawns_on_board, player2_pawns_on_board)
        granted_detetion_move = False

        for mill in found_mills:
            if mill not in self._active_mills:
                self.add_mill(mill)
                if (granted_detetion_move is False):
                    self.grant_deletion_move()
                    self.change_turn()
                    granted_detetion_move = True

        for mill_saved in self._active_mills:
            if mill_saved not in found_mills:
                holding = False
                for pawn in mill_saved:
                    if pawn is self._holding_pawn:
                        holding = True
                if holding is False:
                    self.del_mill(mill_saved)

    def search_mills(self, player1_pawns, player2_pawns):
        list1 = [player1_pawns, player2_pawns]
        return_mills = []
        for player in list1:
            for pawn in player:
                connected_pawns = []
                if pawn.dot_below is not None:
                    for dot in pawn.dot_below.connected_dots:
                        if dot.pawn_on_top is not None and dot.pawn_on_top.player_no_1 is pawn.player_no_1:
                            connected_pawns.append(dot.pawn_on_top)

                for pawn_connected in connected_pawns:
                    distance_between_two = [pawn.dot_below.position[0]-pawn_connected.dot_below.position[0],
                                            pawn.dot_below.position[1]-pawn_connected.dot_below.position[1]]
                    for pawn_potential in player:
                        if pawn_potential is not pawn:
                            distance = [pawn_connected.dot_below.position[0]-pawn_potential.dot_below.position[0],
                                        pawn_connected.dot_below.position[1]-pawn_potential.dot_below.position[1]]
                            if (distance == distance_between_two):
                                potencial_mill = sorted([pawn, pawn_connected, pawn_potential], key=lambda x: self._dots_list.index(x.dot_below))
                                if potencial_mill not in return_mills:
                                    return_mills.append(potencial_mill)
        return return_mills

    def add_mill(self, mill):
        pawn1, pawn2, pawn3 = mill
        pawn1.make_mill(pawn2, pawn3)
        pawn2.make_mill(pawn1, pawn3)
        pawn3.make_mill(pawn1, pawn2)
        self._active_mills.append(mill)

    def del_mill(self, mill):
        pawn1, pawn2, pawn3 = mill
        pawn1.destroy_mill()
        pawn2.destroy_mill()
        pawn3.destroy_mill()
        self._active_mills.remove(mill)

    def grant_deletion_move(self):
        self._deletion_move = True

    def check_end_of_game(self):
        pass

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
            if (self._saved_pos is not None and self._holding_pawn is not None):
                dot = self.check_if_above_dot([self._cursor_x, self._cursor_y])
                move_possible = True

                if self._saved_dot is not None and dot is not None:
                    move_possible = self.check_move(dot)

                if (dot is not None and dot.pawn_on_top is None and move_possible is True):
                    if (self._saved_dot is not None):
                        self._saved_dot.set_pawn_on_top(None)
                    self._holding_pawn.set_position(dot.position)
                    self._holding_pawn.pawn_was_moved()
                    self._holding_pawn.set_dot_below(dot)

                    dot.set_pawn_on_top(self._holding_pawn)

                    if (self._saved_pos != dot.position):
                        if (self._deletion_move is False):
                            self.change_turn()
                else:
                    self._holding_pawn.set_position(self._saved_pos)
            self._holding_pawn = None
            self._saved_pos = None
            self._position_difference = None
            self._saved_dot = None

        elif (self._catch is True):
            is_blue = False
            completed_putting_on_board = True
            if self._holding_pawn is None:
                self._holding_pawn = self.check_if_above_pawn([self._cursor_x, self._cursor_y])

                if (self._player1_turn is True):
                    for pawn in self._player1_pawns:
                        if (pawn.has_been_moved is False):
                            completed_putting_on_board = False
                elif (self._player1_turn is False):
                    for pawn in self._player2_pawns:
                        if (pawn.has_been_moved is False):
                            completed_putting_on_board = False

                if self._holding_pawn is None:
                    self._catch = not self._catch
                    self._render_one_more_frame = True

                elif (self._deletion_move is False and (self._holding_pawn.player_no_1 is not self._player1_turn
                                                        or (self._holding_pawn.has_been_moved is True and completed_putting_on_board is False))):
                    self._catch = not self._catch
                    self._render_one_more_frame = True
                    self._holding_pawn = None

                if (self._deletion_move is True and self._holding_pawn is not None
                   and self._holding_pawn.player_no_1 is not self._player1_turn and self._holding_pawn.has_been_moved is True
                   and len(self._holding_pawn.pawns_in_mill_with) == 0):
                    if self._holding_pawn.player_no_1 is True:
                        self._player1_pawns.remove(self._holding_pawn)
                    elif self._holding_pawn.player_no_1 is False:
                        self._player2_pawns.remove(self._holding_pawn)
                    self._holding_pawn.dot_below.set_pawn_on_top(None)
                    self._holding_pawn = None
                    self._deletion_move = False
                    self._catch = not self._catch
                    self.change_turn()
                    self._render_one_more_frame = True
                elif (self._deletion_move is True and self._holding_pawn is not None
                      and (self._holding_pawn.player_no_1 is self._player1_turn or len(self._holding_pawn.pawns_in_mill_with) != 0)):
                    self._catch = not self._catch
                    self._render_one_more_frame = True
                    self._holding_pawn = None

                if (self._holding_pawn is not None and self._saved_pos is None):
                    self._saved_pos = list(self._holding_pawn.position)
                    self._position_difference = list([self._cursor_x-self._saved_pos[0], self._cursor_y-self._saved_pos[1]])
                    dot = self.check_if_above_dot([self._cursor_x, self._cursor_y])
                    if dot is not None:
                        self._saved_dot = dot
        self.check_mills()
        return is_blue

    def display_frame(self, wrapper):
        self._display.draw_display(wrapper)

    def set_key(self, key):
        self._key = key

    def displayed_one_more_frame(self):
        self._render_one_more_frame = False

    @property
    def one_more_frame(self):
        return self._render_one_more_frame

    @property
    def key(self):
        return self._key

    @property
    def player1_turn(self):
        return self._player1_turn
