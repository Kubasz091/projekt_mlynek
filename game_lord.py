from random import getrandbits
from board import Pawn, Dot
from display import Display
from pawn_placement_saver import PawnPlacementSaver
from bot import Bot


class GameLord:
    """
    The GameLord class represents the main game controller for the Młynek game.

    Attributes:
        _dots_list (list): A list of Dot objects representing the dots on the game board.
        _player1_pawns (list): A list of Pawn objects representing the pawns of player 1.
        _player2_pawns (list): A list of Pawn objects representing the pawns of player 2.
        _active_mills (list): A list of lists containing Pawn objects representing the active mills on the game board.
        _player1_turn (bool): A boolean indicating whether it is currently player 1's turn.
        _started_player1 (bool): A boolean indicating whether player 1 started the game.
        _render_one_more_frame (int): An integer indicating whether to render one more frame.
        _bot (Bot or None): An instance of the Bot class representing the game bot, or None if there is no bot.
        _display (Display): An instance of the Display class representing the game display.
        _placement_saver (PawnPlacementSaver): An instance of the PawnPlacementSaver class for saving pawn placements.
        _cursor_x (int): An integer representing the x-coordinate of the cursor.
        _cursor_y (int): An integer representing the y-coordinate of the cursor.
        _catch (bool): A boolean indicating whether a pawn catch is in progress.
        _deletion_moves (int): An integer representing the number of deletion moves granted.
        _player1_won (bool): A boolean indicating whether player 1 has won the game.
        _player2_won (bool): A boolean indicating whether player 2 has won the game.
        _draw (bool): A boolean indicating whether the game ended in a draw.
        _key (str or None): A string representing the last keyboard key pressed, or None if no key has been pressed.
        _saved_pos (list or None): A list representing the saved position, or None if no position has been saved.
        _position_difference (list or None): A list representing the position difference, or None if no difference has been calculated.
        _holding_pawn (Pawn or None): An instance of the Pawn class representing the pawn being held, or None if no pawn is being held.
        _saved_dot (Dot or None): An instance of the Dot class representing the saved dot, or None if no dot has been saved.
    """
    def __init__(self, size: int, bot: bool, bot_mode: bool):
        """
        Initializes a new instance of the GameLord class.

        Args:
            size (int): The size of the game board.
            bot (bool): A boolean indicating whether to enable the game bot.
            bot_mode (bool): A boolean indicating the mode of the game bot.
        """
        self._dots_list = []
        self._player1_pawns = []
        self._player2_pawns = []
        self._active_mills = []
        self._player1_turn = bool(getrandbits(1))
        self._started_player1 = self._player1_turn
        self._render_one_more_frame = 0

        if bot is True:
            self._bot = Bot(bot_mode, self)
        else:
            self._bot = None

        self._display = Display(size, self)
        self.connect_dots(self._dots_list)

        self._placement_saver = PawnPlacementSaver(40)

        self._cursor_x = 0
        self._cursor_y = 0

        self._catch = False
        self._deletion_moves = 0

        self._player1_won = False
        self._player2_won = False
        self._draw = False

        self._key = None
        self._saved_pos = None
        self._position_difference = None
        self._holding_pawn = None
        self._saved_dot = None

    def change_turn(self):
        """
        Changes the turn to the next player.
        """
        self._player1_turn = not self._player1_turn
        self._placement_saver.count_round_without_mill()

    def add_dot(self, dot: Dot):
        """
        Adds a Dot object to the game board.

        Args:
            dot (Dot): The Dot object to add.
        """
        self._dots_list.append(dot)

    def add_player1_pawn(self, pawn: Pawn):
        """
        Adds a Pawn object to player 1's pawns.

        Args:
            pawn (Pawn): The Pawn object to add.
        """
        self._player1_pawns.append(pawn)

    def add_player2_pawn(self, pawn: Pawn):
        """
        Adds a Pawn object to player 2's pawns.

        Args:
            pawn (Pawn): The Pawn object to add.
        """
        self._player2_pawns.append(pawn)

    def check_if_above_pawn(self, position: list):
        """
        Checks if the given position is above a pawn.

        Args:
            position (list): The position to check.

        Returns:
            Pawn or None: The Pawn object if a pawn is found, None otherwise.
        """
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
        """
        Checks if the given position is above a dot.

        Args:
            position (list): The position to check.

        Returns:
            Dot or None: The Dot object if a dot is found, None otherwise.
        """
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
        """
        Connects the dots on the game board.

        Args:
            dots_list (list): A list of Dot objects representing the dots on the game board.
        """
        keys = self._display._graphic_data.board_data["connected_dots"].keys()
        for key in keys:
            for dot in self._display._graphic_data.board_data["connected_dots"][key]:
                dots_list[key].set_connection(dots_list[dot])
                dots_list[dot].set_connection(dots_list[key])

    def check_move(self, dot: Dot):
        """
        Checks if a move to the given dot is valid.

        Args:
            dot (Dot): The Dot object to check.

        Returns:
            bool: True if the move is valid, False otherwise.
        """
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
        """
        Checks for mills on the game board and updates the active mills.
        """
        player1_pawns_on_board = []
        player2_pawns_on_board = []

        for pawn in self._player1_pawns:
            if pawn.has_been_moved is True and pawn is not self._holding_pawn:
                player1_pawns_on_board.append(pawn)
        for pawn in self._player2_pawns:
            if pawn.has_been_moved is True and pawn is not self._holding_pawn:
                player2_pawns_on_board.append(pawn)

        found_mills = self.search_mills(player1_pawns_on_board, player2_pawns_on_board)

        for mill in found_mills:
            if mill not in self._active_mills:
                self.add_mill(mill)
                self.grant_deletion_move()
                self._placement_saver.mill_occurred()

        for mill_saved in self._active_mills:
            if mill_saved not in found_mills:
                holding = False
                for pawn in mill_saved:
                    if pawn is self._holding_pawn:
                        holding = True
                if holding is False:
                    self.del_mill(mill_saved)

    def search_mills(self, player1_pawns, player2_pawns):
        """
        Searches for mills on the game board.

        Args:
            player1_pawns (list): A list of Pawn objects representing player 1's pawns.
            player2_pawns (list): A list of Pawn objects representing player 2's pawns.

        Returns:
            list: A list of lists containing Pawn objects representing the found mills.
        """
        list1 = [player1_pawns, player2_pawns]
        return_mills = []
        for player in list1:
            for pawn in player:
                connected_dots = pawn.dot_below.connected_dots
                for dot in connected_dots:
                    if dot.pawn_on_top is not None and dot.pawn_on_top.player_no_1 is pawn.player_no_1:
                        distance_between_two = [pawn.dot_below.position[0]-dot.position[0],
                                                pawn.dot_below.position[1]-dot.position[1]]
                        for trd_dot in dot.connected_dots:
                            if (trd_dot.position == [dot.position[0]-distance_between_two[0],
                                                     dot.position[1]-distance_between_two[1]]
                               and trd_dot.pawn_on_top is not None and trd_dot.pawn_on_top.player_no_1 is pawn.player_no_1):
                                potencial_mill = sorted([pawn, dot.pawn_on_top, trd_dot.pawn_on_top], key=lambda x: self._dots_list.index(x.dot_below))
                                if potencial_mill not in return_mills:
                                    return_mills.append(potencial_mill)
        return return_mills

    def add_mill(self, mill):
        """
        Adds a mill to the active mills.

        Args:
            mill (list): A list of Pawn objects representing the mill.
        """
        pawn1, pawn2, pawn3 = mill
        pawn1.make_mill(pawn2, pawn3)
        pawn2.make_mill(pawn1, pawn3)
        pawn3.make_mill(pawn1, pawn2)
        self._active_mills.append(mill)

    def del_mill(self, mill):
        """
        Removes a mill from the active mills.

        Args:
            mill (list): A list of Pawn objects representing the mill.
        """
        pawn1, pawn2, pawn3 = mill
        pawn1.destroy_mill()
        pawn2.destroy_mill()
        pawn3.destroy_mill()
        self._active_mills.remove(mill)

    def grant_deletion_move(self):
        """
        Grants deletion move to the current player
        """
        self._deletion_moves += 1

    def check_end_of_game(self, changed_pawns_placement: bool):
        """
        Checks if the game has ended.

        Args:
            changed_pawns_placement (bool): A boolean indicating whether the pawns placement has changed.
        """
        player1_moved = False
        player2_moved = False

        for pawn in self._player1_pawns:
            if pawn.has_been_moved is True:
                player1_moved = True

        for pawn in self._player2_pawns:
            if pawn.has_been_moved is True:
                player2_moved = True
        if len(self._player1_pawns) < 3 or (len(self.check_possible_moves(self._player1_pawns)) == 0 and player1_moved is True):
            self._player2_won = True
        elif len(self._player2_pawns) < 3 or (len(self.check_possible_moves(self._player2_pawns)) == 0 and player2_moved is True):
            self._player1_won = True

        if self._deletion_moves == 0 and changed_pawns_placement is True:
            current_board_placement = self.build_board_placement_list()

            self._placement_saver.save_placement(current_board_placement)
            self.change_turn()

            if self._placement_saver.check_if_repeated(current_board_placement) >= 3:
                self._draw = True
            elif self._placement_saver.mill_counter >= self._placement_saver.depth:
                self._draw = True

    def build_board_placement_list(self):
        """
        Builds a list representing the current board placement.

        Returns:
            list: A list representing the current board placement.
        """
        return_list = []
        for dot in self._dots_list:
            if dot.pawn_on_top is None:
                return_list.append(0)
            elif dot.pawn_on_top.player_no_1 is True:
                return_list.append(1)
            elif dot.pawn_on_top.player_no_1 is False:
                return_list.append(2)
        return return_list

    def check_possible_moves(self, pawns: list):
        """
        Checks the possible moves for the given pawns.

        Args:
            pawns (list): A list of Pawn objects to check.

        Returns:
            list: A list of lists containing the possible moves.
        """
        possible_moves = []
        unmoved_pawns = []

        for pawn in pawns:
            if pawn.has_been_moved is False:
                unmoved_pawns.append(pawn)
        if len(unmoved_pawns) == 0:
            for pawn in pawns:
                for dot in pawn.dot_below.connected_dots:
                    if dot.pawn_on_top is None:
                        possible_moves.append([pawn, dot])
        else:
            for pawn in unmoved_pawns:
                for dot in self._dots_list:
                    if dot.pawn_on_top is None:
                        possible_moves.append([pawn, dot])
        return possible_moves

    def check_possible_mills(self, player1_pawns, player2_pawns):
        """
        Checks the possible mills for the given pawns.

        Args:
            player1_pawns (list): A list of Pawn objects representing player 1's pawns.
            player2_pawns (list): A list of Pawn objects representing player 2's pawns.

        Returns:
            tuple: A tuple containing two lists of lists representing the possible mills for player 1 and player 2.
        """
        list1 = [player1_pawns, player2_pawns]
        return_mills_player1 = []
        return_mills_player2 = []
        for player in list1:
            for pawn in player:
                connected_dots = pawn.dot_below.connected_dots
                for dot in connected_dots:
                    distance_between_two = [pawn.dot_below.position[0]-dot.position[0],
                                            pawn.dot_below.position[1]-dot.position[1]]
                    trd_dot = None
                    for dot_trd in dot.connected_dots:
                        if dot_trd.position == [dot.position[0]-distance_between_two[0],
                                                dot.position[1]-distance_between_two[1]]:
                            trd_dot = dot_trd
                    if ((dot.pawn_on_top is not None and dot.pawn_on_top.player_no_1 is pawn.player_no_1
                       and
                       trd_dot is not None and (trd_dot.pawn_on_top is None or trd_dot.pawn_on_top.player_no_1 is not pawn.player_no_1))
                       or
                       ((dot.pawn_on_top is None or dot.pawn_on_top.player_no_1 is not pawn.player_no_1)
                       and
                       trd_dot is not None and trd_dot.pawn_on_top is not None and trd_dot.pawn_on_top.player_no_1 is pawn.player_no_1)):
                        possible_mill = sorted([pawn.dot_below, dot, trd_dot], key=lambda x: self._dots_list.index(x))
                        if possible_mill not in return_mills_player1 and list1.index(player) == 0:
                            return_mills_player1.append(possible_mill)
                        elif possible_mill not in return_mills_player2 and list1.index(player) == 1:
                            return_mills_player2.append(possible_mill)

        return return_mills_player1, return_mills_player2

    def keyboard_functionality(self, height: int, width: int):
        """
        Handles the keyboard functionality for the game.

        Args:
            height (int): The height of the game display.
            width (int): The width of the game display.
        """
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

        self._cursor_x = max(4, self._cursor_x)
        self._cursor_x = min(width-6, self._cursor_x)

        self._cursor_y = max(2, self._cursor_y)
        self._cursor_y = min(height-4, self._cursor_y)

        return self._cursor_x, self._cursor_y

    def game_mechanics(self):
        """
        Executes the game mechanics, including pawn movement, capturing, and checking for mills.

        Returns:
            bool: True if the e key has been activated, False if it wasn't
        """
        is_off = True
        changed_pawns_placement = False
        if self._catch is True and self._holding_pawn is not None:
            self._holding_pawn.set_position([self._cursor_x-self._position_difference[0],
                                             self._cursor_y-self._position_difference[1]])

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

                    if (self._saved_pos != dot.position and self._deletion_moves == 0):
                        changed_pawns_placement = True
                        self._render_one_more_frame += 1
                else:
                    self._holding_pawn.set_position(self._saved_pos)
            self._holding_pawn = None
            self._saved_pos = None
            self._position_difference = None
            self._saved_dot = None

        elif (self._catch is True):
            is_off = False
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
                    self._render_one_more_frame += 1
                elif (self._deletion_moves == 0
                      and
                      (self._holding_pawn.player_no_1 is not self._player1_turn
                       or
                       (self._holding_pawn.has_been_moved is True and completed_putting_on_board is False))):
                    self._catch = not self._catch
                    self._holding_pawn = None
                    self._render_one_more_frame += 1
                has_pawns_not_in_mill = False

                if self._player1_turn is True:
                    for pawn in self._player2_pawns:
                        if len(pawn.pawns_in_mill_with) == 0 and pawn.has_been_moved is True:
                            has_pawns_not_in_mill = True
                elif self._player1_turn is False:
                    for pawn in self._player1_pawns:
                        if len(pawn.pawns_in_mill_with) == 0 and pawn.has_been_moved is True:
                            has_pawns_not_in_mill = True

                if (self._deletion_moves > 0 and self._holding_pawn is not None
                   and self._holding_pawn.player_no_1 is not self._player1_turn and self._holding_pawn.has_been_moved is True
                   and (len(self._holding_pawn.pawns_in_mill_with) == 0 or has_pawns_not_in_mill is False)):
                    if self._holding_pawn.player_no_1 is True:
                        self._player1_pawns.remove(self._holding_pawn)
                    elif self._holding_pawn.player_no_1 is False:
                        self._player2_pawns.remove(self._holding_pawn)
                    self._holding_pawn.dot_below.set_pawn_on_top(None)
                    self._holding_pawn = None
                    self._deletion_moves -= 1
                    self._catch = not self._catch
                    self._render_one_more_frame += 1
                    changed_pawns_placement = True
                elif (self._deletion_moves > 0 and self._holding_pawn is not None
                      and (self._holding_pawn.player_no_1 is self._player1_turn or len(self._holding_pawn.pawns_in_mill_with) != 0
                           or self._holding_pawn.has_been_moved is False)):
                    self._catch = not self._catch
                    self._holding_pawn = None
                    self._render_one_more_frame += 1
                if (self._holding_pawn is not None and self._saved_pos is None):
                    self._saved_pos = list(self._holding_pawn.position)
                    self._position_difference = list([self._cursor_x-self._saved_pos[0], self._cursor_y-self._saved_pos[1]])
                    dot = self.check_if_above_dot([self._cursor_x, self._cursor_y])
                    if dot is not None:
                        self._saved_dot = dot
        if self._bot is not None and self._player1_turn is True:
            changed_pawns_placement = self._bot.make_move(self._player1_pawns, self._player2_pawns)
        self.check_mills()
        self.check_end_of_game(changed_pawns_placement)
        return is_off

    def display_frame(self, wrapper):
        """
        Draw the current game state on the display.

        Parameters:
        wrapper (object): A wrapper object for the display.
        """
        self._display.draw_display(wrapper)

    def set_key(self, key):
        """
        Set the key for the game.

        Parameters:
        key (str): The key to be set.
        """
        self._key = key

    def displayed_one_more_frame(self):
        """
        Decrease the count of frames to be rendered extra by one.
        """
        self._render_one_more_frame -= 1

    @property
    def deletion_moves(self):
        """
        Return the deletion moves in the game.

        Returns:
        int: The number of deletion moves.
        """
        return self._deletion_moves

    @property
    def one_more_frame(self):
        """
        Return the count of frames to be rendered.

        Returns:
        int: The count of frames to be rendered.
        """
        return self._render_one_more_frame

    @property
    def key(self):
        """
        Return the key of the game.

        Returns:
        str: The key of the game.
        """
        return self._key

    @property
    def player1_turn(self):
        """
        Check if it's player 1's turn.

        Returns:
        bool: True if it's player 1's turn, False otherwise.
        """
        return self._player1_turn
