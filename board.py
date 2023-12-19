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
    no_of_sqr_1_size_3_board = {
        "dot": [(0, 0), (12, 0), (24, 0),
                (0, 6), (12, 6), (24, 6),
                (0, 12), (12, 12), (24, 12)],

        "horizontal_line": [(6, 1), (18, 1),
                            (6, 7), (18, 7),
                            (6, 13), (18, 13)],

        "vertical_line": [(2, 3), (14, 3), (26, 3),
                          (2, 9), (14, 9), (26, 9)],

        "diagonal_l_r": [(5, 2),
                         (17, 8)],

        "diagonal_r_l": [(17, 2),
                         (5, 8)]
        }
    board_display_list = create_board_display_list(terminal_size=terminal_size)
    if (no_of_sqr == 1):
        over_write_display(graphics_dict,
                           terminal_size,
                           no_of_sqr_1_size_3_board,
                           board_display_list)


    elif (no_of_sqr == 2):
        pass
        # current_position = [0, 0]
        # append_display(str_dot, (x_size, y_size), (6, current_position, [24, 24]), return_list, [False, True])

        # current_position = [12, 6]
        # append_display(str_dot, (42, y_size), (6, current_position, [12, 12]), return_list, [False, True])

        # current_position = [0, 12]
        # str_added_01 = []
        # for row in str_dot:
        #     if (str_dot.index(row) == 1):
        #         str_added_01.append(row + horizontal_line[0] + row)
        #     else:
        #         str_added_01.append(row + ' ' * len(horizontal_line[0]) + row)
        # append_display(str_added_01, (x_size, y_size), (2, current_position, [36, 0]), return_list, [False, True])

        # current_position = [6, 1]
        # str_added_02 = [horizontal_line[0] * 3]
        # append_display(str_added_02, (x_size, y_size), (4, current_position, [24, 24]), return_list, [False, True])

        # current_position = [18, 7]
        # str_added_03 = [horizontal_line[0] * 2]
        # append_display(horizontal_line, (42, y_size), (4, current_position, [12, 12]), return_list, [False, True])

        # current_position = [14, 9]
        # append_display(vertical_line, (42, y_size), (4, current_position, [24, 6]), return_list, [False, True])

        # current_position = [2, 3]
        # str_added_04 = []
        # for i in range(9):
        #     str_added_04.append(vertical_line[0])
        # append_display(str_added_04, (x_size, y_size), (4, current_position, [48, 12]), return_list, [False, True])

        # current_position = [26, 3]
        # append_display(vertical_line, (32, y_size), (2, current_position, [10, 18]), return_list, [False, True])
    return board_display_list

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
