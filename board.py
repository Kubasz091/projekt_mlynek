import time

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
    return (15 + (12 * no_of_sqr - 1), (15 + (12 * no_of_sqr - 1)) * 2)


def append_display_v2(str_to_print: list, size: tuple, number_to_print: int, coordinates: list, return_list: list):
    if (len(coordinates) != number_to_print):
        raise ValueError("give the righ ammount of coordinates")
    for item in range(number_to_print):
        temp_pos = list(coordinates[item])
        for row in str_to_print:
            if temp_pos[0] > size[0] or temp_pos[1] > size[1]:
                raise ValueError("Outside of bounds")
            for char in row:
                if (char != ' '):
                    return_list[temp_pos[1]][temp_pos[0]] = char
                temp_pos[0] += 1
            temp_pos[1] += 1
            temp_pos[0] = coordinates[item][0]


def append_display(str_to_print: list, size: tuple, vals: tuple, return_list: list, directions: list):
    '''
    vals = (no_of_items_to_print, start_position, print_finish_skip)
    start_position = [start_x, start_y]
    print_finish_skip = [x_skip, y_skip]
    size = (x_size, y_size)
    directions = (is_diagonal, is_going_up)
    '''
    start_x = vals[1][0]
    for item_to_print in range(vals[0]):
        if (vals[1][0] > (size[0] - 1)):
            vals[1][0] = start_x
            vals[1][1] += vals[2][1]
        temp_pos = list(vals[1])
        for row in str_to_print:
            for char in row:
                if (char != ' '):
                    return_list[temp_pos[1]][temp_pos[0]] = char
                temp_pos[0] += 1
            if (directions[1] is True):
                temp_pos[1] += 1
            elif (directions[1] is False):
                temp_pos[1] -= 1
            temp_pos[0] = vals[1][0]
        vals[1][0] += vals[2][0]
        if (directions[0] is True):
            vals[1][1] += vals[2][1]


def build_board(diagonals: bool, no_of_sqr: int, no_of_spots: int, terminal_size: tuple):
    graphics_dict = {
                     "dot": [' ▄██▄ ',
                             '▐████▌',
                             ' ▀██▀ '],
                     "horizontal_line": ['══════'],
                     "vertical_line": ['││',
                                       '││',
                                       '││'],
                     "diagonal_l_r": ['▄       ',
                                      ' ▀▄     ',
                                      '   ▀▄   ',
                                      '     ▀▄ ',
                                      '       ▀'],
                     "diagonal_r_l": ['       ▄▀',
                                      '     ▄▀  ',
                                      '   ▄▀    ',
                                      ' ▄▀      ',
                                      '▀        ']
                    }

    str_dot = [
        ' ▄██▄ ',
        '▐████▌',
        ' ▀██▀ '
    ]
    horizontal_line = ['══════']
    vertical_line = [
        '││',
        '││',
        '││'
    ]
    diagonal_left_to_right = [
        '▄       ',
        ' ▀▄     ',
        '   ▀▄   ',
        '     ▀▄ ',
        '       ▀'
    ]
    diagonal_right_to_left = [
        '       ▄▀',
        '     ▄▀  ',
        '   ▄▀    ',
        ' ▄▀      ',
        '▀        '
    ]
    x_size, y_size = terminal_size
    return_list = []
    for row in range(y_size):
        _ = []
        for char in range(x_size):
            _.append(' ')
        return_list.append(_)

    if (no_of_sqr == 1):
        no_of_sqr_1_size_3_board = {"str"}
        dot_list = [(0, 0), (12, 0), (24, 0),
                    (0, 6), (12, 6), (24, 6),
                    (0, 12), (12, 12), (24, 12)]

        horizontal_line_list = [(6, 1), (18, 1),
                                (6, 7), (18, 7),
                                (6, 13), (18, 13)]

        vertical_line_list = [(2, 3), (14, 3), (26, 3),
                              (2, 9), (14, 9), (26, 9)]

        diagonal_left_to_right_list = [(5, 2),
                                       (17, 8)]

        diagonal_right_to_left_list = [(17, 2),
                                       (5, 8)]

        append_display_v2(str_dot, (x_size, y_size), 9, dot_list, return_list)
        append_display_v2(horizontal_line, (x_size, y_size), 6, horizontal_line_list, return_list)
        append_display_v2(vertical_line, (x_size, y_size), 6, vertical_line_list, return_list)
        append_display_v2(diagonal_left_to_right, (x_size, y_size), 2, diagonal_left_to_right_list, return_list)
        append_display_v2(diagonal_right_to_left, (x_size, y_size), 2, diagonal_right_to_left_list, return_list)

        
    elif (no_of_sqr == 2):
        current_position = [0, 0]
        append_display(str_dot, (x_size, y_size), (6, current_position, [24, 24]), return_list, [False, True])

        current_position = [12, 6]
        append_display(str_dot, (42, y_size), (6, current_position, [12, 12]), return_list, [False, True])

        current_position = [0, 12]
        str_added_01 = []
        for row in str_dot:
            if (str_dot.index(row) == 1):
                str_added_01.append(row + horizontal_line[0] + row)
            else:
                str_added_01.append(row + ' ' * len(horizontal_line[0]) + row)
        append_display(str_added_01, (x_size, y_size), (2, current_position, [36, 0]), return_list, [False, True])

        current_position = [6, 1]
        str_added_02 = [horizontal_line[0] * 3]
        append_display(str_added_02, (x_size, y_size), (4, current_position, [24, 24]), return_list, [False, True])

        current_position = [18, 7]
        str_added_03 = [horizontal_line[0] * 2]
        append_display(horizontal_line, (42, y_size), (4, current_position, [12, 12]), return_list, [False, True])

        current_position = [14, 9]
        append_display(vertical_line, (42, y_size), (4, current_position, [24, 6]), return_list, [False, True])

        current_position = [2, 3]
        str_added_04 = []
        for i in range(9):
            str_added_04.append(vertical_line[0])
        append_display(str_added_04, (x_size, y_size), (4, current_position, [48, 12]), return_list, [False, True])

        current_position = [26, 3]
        append_display(vertical_line, (32, y_size), (2, current_position, [10, 18]), return_list, [False, True])
    return return_list

list1 = build_board(True, 1, 9, (30, 15))
for row in list1:
    _ = ''
    for char in row:
        _ += char
    print(_)

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
