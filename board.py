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
        guess = guess_what_user_meant(number=number, possible_numbers=possible_numbers)
        super().__init__(self, f"Wrong board size given, did you mean: {guess}?")


class Board:
    def __init__(self, size: int):
        self._possible_sizes = [3, 6, 9, 12]
        if size not in self._possible_sizes:
            raise WrongBoardSize(number=size, possible_numbers=self._possible_sizes)
        self._size = size
        self._diagonals = self._size in [3, 12]
        self._no_of_sqr = [1, 2, 3, 3][self._possible_sizes.index(self._size)]
        self._no_of_spots = [9, 16, 24, 24][self._possible_sizes.index(self._size)]
        self._terminal_size = calc_terminal_board_size(self._no_of_sqr)

    def __str__(self):
        return f'Board of size: {self._size}'

    @property
    def size(self):
        return self._size

    @property
    def diagonals(self):
        return self._diagonals

    @property
    def number_of_squares(self):
        return self._no_of_sqr

    @property
    def terminal_size(self):
        return self._terminal_size

    @property
    def no_of_spots(self):
        return self._no_of_spots
