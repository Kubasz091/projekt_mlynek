def guess_what_user_meant(number: int, possible_numbers: list):
    guess = 0
    i = 0
    for num in possible_numbers:
        if abs(number - num) < abs(number - possible_numbers[guess]):
            guess = i
        i += 1
    return possible_numbers[guess]


def calc_terminal_board_size(no_of_sqr: int):
    '''
    returns (x, y) sizes in terminal characters
    '''
    return ((15 + (12 * (no_of_sqr - 1))) * 2, 15 + (12 * (no_of_sqr - 1)))


class WrongBoardSize(Exception):
    def __init__(self, number: int, possible_numbers: list):
        guess = guess_what_user_meant(number, possible_numbers)
        super().__init__(self, f"Wrong board size given, did you mean: {guess}?")


class Board:
    def __init__(self, size: int):
        possible_sizes = [3, 6, 9, 12]
        no_of_sqr = [1, 2, 3, 3][possible_sizes.index(size)]

        if size not in possible_sizes:
            raise WrongBoardSize(number=size, possible_numbers=possible_sizes)
        self._size = size
        self._terminal_size = calc_terminal_board_size(no_of_sqr)
        self._no_of_sqr = no_of_sqr

    def __str__(self):
        return f'Board of size: {self._size}'

    @property
    def size(self):
        return self._size

    @property
    def terminal_size(self):
        return self._terminal_size

    @property
    def no_of_sqr(self):
        return self._no_of_sqr


class Pawn:
    def __init__(self, position: list, player_no_1: bool):
        self._player_no_1 = player_no_1
        self._position = list(position)
        self._has_been_moved = False

    def __str__(self):
        return f'This is pawn of player {self._player_no}, at position: x:{int(self._position[0]/2)}, y:{self._position[1]}'

    def set_position(self, position: list):
        self._position = position

    def pawn_was_moved(self):
        self._has_been_moved = True

    @property
    def has_been_moved(self):
        return self._has_been_moved

    @property
    def player_no_1(self):
        return self._player_no_1

    @property
    def position(self):
        return (self._position)


class Dot:
    def __init__(self, position: list):
        self._position = position
        self._dots_connected_with = []
        self._pawn_on_top = None

    def set_connection(self, dot):
        self._dots_connected_with.append(dot)

    def set_pawn_on_top(self, pawn):
        self._pawn_on_top = pawn

    @property
    def position(self):
        return self._position

    @property
    def pawn_on_top(self):
        return self._pawn_on_top

    @property
    def connected_dots(self):
        return self._dots_connected_with
