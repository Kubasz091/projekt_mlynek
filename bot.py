from random import randint
from time import sleep


class Bot:
    """
    A class to represent a bot player in a game.
    """
    def __init__(self, random_moves: bool, game_lord):
        """
        Initialize the bot with its strategy and GameLord.

        Parameters:
        random_moves (bool): If True, the bot makes random moves. Otherwise, it follows a specific strategy.
        game_lord (GameLord): The ruler of the game.
        """
        self._random_moves = random_moves
        self._game_lord = game_lord

    def make_move(self, player1_pawns, player2_pawns):
        """
        Make a move for the bot.

        Parameters:
        player1_pawns (list): The pawns of player 1.
        player2_pawns (list): The pawns of player 2.
        """
        self._game_lord._render_one_more_frame += 1
        if self._random_moves is True:
            self.random_move(player1_pawns, player2_pawns)
            return True
        else:
            player1_pawns_on_board = []
            player2_pawns_on_board = []

            for pawn in player1_pawns:
                if pawn.has_been_moved is True:
                    player1_pawns_on_board.append(pawn)
            for pawn in player2_pawns:
                if pawn.has_been_moved is True:
                    player2_pawns_on_board.append(pawn)

            player1_possible_mills, player2_possible_mills = self._game_lord.check_possible_mills(player1_pawns_on_board, player2_pawns_on_board)

            done_move = False

            if (self._game_lord.deletion_moves == 0):
                possible_moves = self._game_lord.check_possible_moves(player1_pawns)
                if len(player1_possible_mills) > 0:
                    doable_mills = []
                    for mill in player1_possible_mills:
                        for dot in mill:
                            if dot.pawn_on_top is None:
                                doable_mills.append(dot)
                    if len(doable_mills) > 0:
                        for option in range(len(doable_mills)):
                            for move in possible_moves:
                                if move[1].position == doable_mills[option].position:
                                    if move[0].dot_below is not None:
                                        move[0].dot_below.set_pawn_on_top(None)
                                    move[0].set_position(move[1].position)
                                    move[0].pawn_was_moved()
                                    move[0].set_dot_below(move[1])

                                    move[1].set_pawn_on_top(move[0])
                                    done_move = True
                                if done_move is True:
                                    break
                            if done_move is True:
                                break
                if len(player2_possible_mills) > 0 and done_move is False:
                    doable_mills = []
                    for mill in player2_possible_mills:
                        for dot in mill:
                            if dot.pawn_on_top is None:
                                doable_mills.append(dot)
                    if len(doable_mills) > 0:
                        for option in range(len(doable_mills)):
                            for move in possible_moves:
                                if move[1].position == doable_mills[option].position:
                                    if move[0].dot_below is not None:
                                        move[0].dot_below.set_pawn_on_top(None)
                                    move[0].set_position(move[1].position)
                                    move[0].pawn_was_moved()
                                    move[0].set_dot_below(move[1])

                                    move[1].set_pawn_on_top(move[0])
                                    done_move = True
                                if done_move is True:
                                    break
                            if done_move is True:
                                break
                if done_move is False:
                    mill_destroying_moves = []
                    for move in possible_moves:
                        if len(move[0].pawns_in_mill_with) > 0:
                            mill_destroying_moves.append(move)
                    if len(mill_destroying_moves) < len(possible_moves):
                        for move in mill_destroying_moves:
                            if move in possible_moves:
                                possible_moves.remove(move)

                    mill_allowing_moves = []
                    for move in possible_moves:
                        for mill in player2_possible_mills:
                            for dot in mill:
                                if dot.pawn_on_top is not None and dot.pawn_on_top.player_no_1 is True and dot.pawn_on_top is move[0]:
                                    mill_allowing_moves.append(move)
                    if len(mill_allowing_moves) < len(possible_moves):
                        for move in mill_allowing_moves:
                            if move in possible_moves:
                                possible_moves.remove(move)

                    move_number = randint(0, len(possible_moves)-1)
                    move = possible_moves[move_number]
                    if (move[0].dot_below is not None):
                        move[0].dot_below.set_pawn_on_top(None)
                    move[0].set_position(move[1].position)
                    move[0].pawn_was_moved()
                    move[0].set_dot_below(move[1])

                    move[1].set_pawn_on_top(move[0])
                    done_move = True
            elif (self._game_lord.deletion_moves > 0):
                sleep(1)
                possible_pawns_to_delete = []
                for pawn in player2_pawns_on_board:
                    if len(pawn.pawns_in_mill_with) == 0:
                        possible_pawns_to_delete.append(pawn)
                if len(player2_possible_mills) > 0:
                    doable_deletions = []
                    for mill in player2_possible_mills:
                        for dot in mill:
                            if dot.pawn_on_top is None:
                                other_two_dots = mill
                                other_two_dots.remove(dot)
                                for dot_two in other_two_dots:
                                    if dot_two.pawn_on_top in possible_pawns_to_delete or len(possible_pawns_to_delete) == 0:
                                        doable_deletions.append(dot_two)
                    if len(doable_deletions) > 0:
                        move_number = randint(0, len(doable_deletions)-1)
                        pawn_to_delete = doable_deletions[move_number].pawn_on_top

                        player2_pawns.remove(pawn_to_delete)
                        pawn_to_delete.dot_below.set_pawn_on_top(None)

                        self._game_lord._deletion_moves -= 1
                        done_move = True
                if len(player1_possible_mills) > 0 and done_move is False:
                    doable_deletions = []
                    for mill in player1_possible_mills:
                        for dot in mill:
                            if dot.pawn_on_top is not None and dot.pawn_on_top.player_no_1 is False and len(dot.pawn_on_top.pawns_in_mill_with) == 0:
                                doable_deletions.append(dot)
                    if len(doable_deletions) > 0:
                        move_number = randint(0, len(doable_deletions)-1)
                        pawn_to_delete = doable_deletions[move_number].pawn_on_top

                        player2_pawns.remove(pawn_to_delete)
                        pawn_to_delete.dot_below.set_pawn_on_top(None)

                        self._game_lord._deletion_moves -= 1
                        done_move = True
                if done_move is False:
                    self.random_move(player1_pawns, player2_pawns)
                    done_move = True
                self._game_lord._render_one_more_frame += 1
            return True

    def random_move(self, player1_pawns, player2_pawns):
        """
        Make a random move for the bot.

        Parameters:
        player1_pawns (list): The pawns of player 1.
        player2_pawns (list): The pawns of player 2.
        """
        if (self._game_lord.deletion_moves == 0):
            possible_moves = self._game_lord.check_possible_moves(player1_pawns)
            move_number = randint(0, len(possible_moves)-1)
            move = possible_moves[move_number]
            if (move[0].dot_below is not None):
                move[0].dot_below.set_pawn_on_top(None)
            move[0].set_position(move[1].position)
            move[0].pawn_was_moved()
            move[0].set_dot_below(move[1])

            move[1].set_pawn_on_top(move[0])
        elif (self._game_lord.deletion_moves > 0):
            possible_pawns_to_delete = []
            for pawn in player2_pawns:
                if pawn.has_been_moved is True and len(pawn.pawns_in_mill_with) == 0:
                    possible_pawns_to_delete.append(pawn)

            if len(possible_pawns_to_delete) == 0:
                for pawn in player2_pawns:
                    if pawn.has_been_moved is True:
                        possible_pawns_to_delete.append(pawn)
            move_number = randint(0, len(possible_pawns_to_delete)-1)
            pawn_to_delete = possible_pawns_to_delete[move_number]

            player2_pawns.remove(pawn_to_delete)
            pawn_to_delete.dot_below.set_pawn_on_top(None)

            self._game_lord._deletion_moves -= 1

    @property
    def random(self):
        """
        Return the bot's strategy.

        Returns:
        bool: If True, the bot makes random moves. Otherwise, it follows a specific strategy.
        """
        return self._random_moves
