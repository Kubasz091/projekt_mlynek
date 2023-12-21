from board import Board
from graphic_data import GraphicData
from time import sleep
import os


def create_display_list(board_terminal_size: tuple):
    return_list = []
    for row in range(board_terminal_size[1]):
        _ = []
        for char in range(board_terminal_size[0]):
            _.append(' ')
        return_list.append(_)
    return return_list


def build_board(board_terminal_size: tuple, graphic_data: GraphicData):

    board_display_list = create_display_list(board_terminal_size)

    over_write_display(graphic_data.graphics_data,
                       board_terminal_size,
                       graphic_data.board_data,
                       board_display_list)

    return board_display_list


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


def create_full_display_list(board_display: list, size: int, graphic_data: GraphicData):
    board_height = len(board_display)
    pawn_height = len(graphic_data.graphics_data["pawn_player1"])
    pawn_width = len(graphic_data.graphics_data["pawn_player1"][0])
    pawn_columns = (((pawn_height + 2) * size) // board_height)
    if ((((pawn_height + 2) * size) % board_height) != 0):
        pawn_columns += 1
    if (pawn_columns == 1):
        pawn_columns += 1
    x_board_size = len(board_display[0])
    single_player_panel_x_size = (pawn_width + 2) * pawn_columns
    x_display_size = x_board_size + (2 * single_player_panel_x_size)

    dict_pawn = {"pawn_player1": [], "pawn_player2": []}
    no_of_pawns_in_a_column = (size // pawn_columns)
    if (size % pawn_columns) != 0:
        no_of_pawns_in_a_column += 1

    start_y = int((board_height - (no_of_pawns_in_a_column * (pawn_height + 1))) / 2) + 1
    headline_x = x_display_size - (pawn_columns * (pawn_width + 2))

    temp_pos = [0, start_y]
    for pawn in range(size):
        if (temp_pos[0] > (single_player_panel_x_size - 1)):
            temp_pos[1] += pawn_height + 1
            temp_pos[0] = 0
        dict_pawn["pawn_player1"].append((temp_pos[0], temp_pos[1]))
        temp_pos[0] += (pawn_width + 2)

    temp_pos = [x_display_size - (pawn_width + 2), start_y]
    for pawn in range(size):
        if (temp_pos[0] < (x_display_size - single_player_panel_x_size - 1)):
            temp_pos[1] += pawn_height + 1
            temp_pos[0] = x_display_size - (pawn_width + 2)
        dict_pawn["pawn_player2"].append((temp_pos[0], temp_pos[1]))
        temp_pos[0] -= (pawn_width + 2)

    board_display_list_temp = []
    for row in board_display:
        _ = ''
        for char in row:
            _ += char
        board_display_list_temp.append(_)

    return_list = create_display_list((x_display_size, board_height))
    print(len(return_list[0]), len(return_list))
    over_write_display({"board_display": board_display_list_temp}, (x_display_size, board_height),
                       {"board_display": [((single_player_panel_x_size - 1), 0)]}, return_list=return_list)
    over_write_display(graphic_data.graphics_data, (x_display_size, board_height),
                       dict_pawn, return_list=return_list)
    over_write_display({"player1": ["Player 1", " Pawns: "], "player2": ["Player 2", " Pawns: "]}, (x_display_size, board_height),
                       {"player1": [(0, start_y - 3)], "player2": [(headline_x, start_y - 3)]}, return_list)
    return return_list, dict_pawn


class Display:
    def __init__(self, board: Board):
        self._board = board
        self._graphic_data = GraphicData(board.size)
        self._board_display_list = build_board(board.terminal_size, self._graphic_data)
        self._full_display_list, self._pawns_locations = create_full_display_list(self._board_display_list,
                                                                                  board.size, self._graphic_data)

    def __str__(self):
        return_str = ''
        for row in self._full_display_list:
            _ = ''
            for char in row:
                _ += char
            _ += '\n'
            return_str += _
        return return_str


os.system('cls' if os.name == 'nt' else 'clear')
print(Display(Board(3)))
sleep(3)

os.system('cls' if os.name == 'nt' else 'clear')
print(Display(Board(6)))
sleep(4)

os.system('cls' if os.name == 'nt' else 'clear')
print(Display(Board(9)))
sleep(5)

os.system('cls' if os.name == 'nt' else 'clear')
print(Display(Board(12)))
sleep(10)
