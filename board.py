from board_data import BoardData
import os
from time import sleep


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


def over_write_display(graphics_dict: dict, size: tuple, board_to_print: dict, return_list: list):
    indv_items_to_print = list(board_to_print.keys())
    for item in indv_items_to_print:
        for position in board_to_print[item]:
            temp_pos = list(position)
            for row in graphics_dict[item]:
                if (temp_pos[0] > size[0]
                   or temp_pos[0] < 0
                   or temp_pos[1] > size[1]
                   or temp_pos[1] < 0):
                    raise ValueError("Outside of bounds")
                for char in row:
                    if (char != " "):
                        return_list[temp_pos[1]][temp_pos[0]] = char
                    temp_pos[0] += 1
                temp_pos[1] += 1
                temp_pos[0] = position[0]


def create_board_display_list(terminal_size: tuple):
    return_list = []
    for row in range(terminal_size[1]):
        _ = []
        for char in range(terminal_size[0]):
            _.append(' ')
        return_list.append(_)
    return return_list


def build_board(diagonals: bool, no_of_sqr: int, terminal_size: tuple):
    board_display_list = create_board_display_list(terminal_size=terminal_size)
    board_Data = BoardData(diagonals=diagonals, no_of_sqr=no_of_sqr)

    over_write_display(board_Data.graphics_data,
                       terminal_size,
                       board_Data.board_data,
                       board_display_list)
    return board_display_list


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
        self._display_list = build_board(self._diagonals, self._no_of_sqr, self._terminal_size)

    def __str__(self):
        return_str = ''
        for row in self._display_list:
            _ = ''
            for char in row:
                _ += char
            _ += '\n'
            return_str += _
        return return_str

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
    def display_list(self):
        return self._display_list


os.system('cls' if os.name == 'nt' else 'clear')
print(Board(3))
sleep(3)

os.system('cls' if os.name == 'nt' else 'clear')
print(Board(6))
sleep(4)

os.system('cls' if os.name == 'nt' else 'clear')
print(Board(9))
sleep(5)

os.system('cls' if os.name == 'nt' else 'clear')
print(Board(12))
sleep(10)
