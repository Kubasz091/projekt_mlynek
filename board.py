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

    def __str__(self):
        return f'Board of size: {self._size}'

    @property
    def size(self):
        return self._size

    @property
    def terminal_size(self):
        return self._terminal_size


class Pawn:
    def __init__(self, position: list, player_no: int):
        if (player_no not in [1, 2]):
            raise ValueError("wrong player number given")
        self._player_no = player_no
        self._position = list(position)

    @property
    def player_no(self):
        return self._player_no

    @property
    def position(self):
        return self._position
