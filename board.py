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


def append_display(str_to_print: list, size: tuple, vals: tuple, return_list: list):
    '''
    vals = (no_of_items_to_print, start_position, print_finish_skip)
    start_position = [start_x, start_y]
    print_finish_skip = [x_skip, y_skip]
    size = (x_size, y_size)
    '''
    start_x = vals[1][0]
    for item_to_print in range(vals[0]):
        if (vals[1][0] > (size[0] - 1)):
            vals[1][0] = start_x
            vals[1][1] += vals[2][1]
        temp_pos = list(vals[1])
        for row in str_to_print:
            for char in row:
                return_list[temp_pos[1]][temp_pos[0]] = char
                # print(temp_pos)
                temp_pos[0] += 1
            temp_pos[1] += 1
            temp_pos[0] = vals[1][0]
        vals[1][0] += vals[2][0]


def build_board(diagonals: bool, no_of_sqr: int, no_of_spots: int, terminal_size: tuple):
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
    x_size, y_size = terminal_size
    return_list = []
    for row in range(y_size):
        _ = []
        for char in range(x_size):
            _.append(' ')
        return_list.append(_)

    current_position = [0, 0]
    append_display(str_dot, (x_size, y_size), (9, current_position, [12, 6]), return_list=return_list)
    # for dot in range(no_of_spots):
    #     if (current_position[0] > (x_size - 1)):
    #         current_position[0] = 0
    #         current_position[1] += 6
    #     temp_pos = list(current_position)
    #     for row in str_dot:
    #         for char in row:
    #             return_list[temp_pos[1]][temp_pos[0]] = char
    #             # print(temp_pos)
    #             temp_pos[0] += 1
    #         temp_pos[1] += 1
    #         temp_pos[0] = current_position[0]
    #     current_position[0] += 12

    current_position = [6, 1]
    append_display(horizontal_line, (x_size, y_size), (6, current_position, [12, 6]), return_list=return_list)
    # print('rendering horizontal lines')
    # for line1 in range(6):
    #     if (current_position[0] > (x_size - 1)):
    #         current_position[0] = 6
    #         current_position[1] += 6
    #     temp_pos = list(current_position)
    #     for char in horizontal_line:
    #         return_list[temp_pos[1]][temp_pos[0]] = char
    #         # print(temp_pos)
    #         temp_pos[0] += 1
    #     current_position[0] += 12

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
