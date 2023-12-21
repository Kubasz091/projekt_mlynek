from board import Board
from graphic_data import GraphicData
from time import sleep
import os


class CoordinatesError(Exception):
    def __init__(self, text):
        super().__init__(self, text)


def create_display_list(terminal_size: tuple):
    return_list = []
    for row in range(terminal_size[1]):
        _ = []
        for char in range(terminal_size[0]):
            _.append(' ')
        return_list.append(_)
    return return_list


def print_item_in_coordinates(item: list, coordinates: tuple, display_list: list):
    if (coordinates[0] < 0 or coordinates[1] < 0):
        raise CoordinatesError("Coordinates cannot be negative!")
    if ((coordinates[0] + len(item[0])) > len(display_list[0])
       or (coordinates[1] + len(item)) > len(display_list)):
        raise CoordinatesError("Some part of the object outside of display bounds!")
    temp_pos = list(coordinates)
    for row in item:
        for char in row:
            if (char != " "):
                display_list[temp_pos[1]][temp_pos[0]] = char
            temp_pos[0] += 1
        temp_pos[1] += 1
        temp_pos[0] = coordinates[0]


def print_miltiple_items(graphics_dict: dict, items_with_positions: dict, return_list: list):
    indv_items_to_print = list(items_with_positions.keys())
    for item in indv_items_to_print:
        for position in items_with_positions[item]:
            print_item_in_coordinates(graphics_dict[item], position, return_list)


def create_full_display_list(graphic_data: GraphicData):
    board_height = graphic_data.board_data["dot"][-1][1] + 3
    board_width = graphic_data.board_data["dot"][2][0] + 6

    pawn_height = len(graphic_data.graphics_data["pawn_player1"])
    pawn_width = len(graphic_data.graphics_data["pawn_player1"][0])
    pawn_columns = (((pawn_height + 2) * graphic_data.size) // board_height)
    if ((((pawn_height + 2) * graphic_data.size) % board_height) != 0):
        pawn_columns += 1
    if (pawn_columns == 1):
        pawn_columns += 1

    single_player_panel_x_size = (pawn_width + 2) * pawn_columns
    x_display_size = board_width + (2 * single_player_panel_x_size)
    print((single_player_panel_x_size * 2) + board_width)

    dict_pawn = {"pawn_player1": [], "pawn_player2": []}
    no_of_pawns_in_a_column = (graphic_data.size // pawn_columns)
    if (graphic_data.size % pawn_columns) != 0:
        no_of_pawns_in_a_column += 1

    start_y = int((board_height - (no_of_pawns_in_a_column * (pawn_height + 1))) / 2) + 1
    headline_x = x_display_size - (pawn_columns * (pawn_width + 2))

    temp_pos = [0, start_y]
    for pawn in range(graphic_data.size):
        if (temp_pos[0] > (single_player_panel_x_size - 1)):
            temp_pos[1] += pawn_height + 1
            temp_pos[0] = 0
        dict_pawn["pawn_player1"].append((temp_pos[0], temp_pos[1]))
        temp_pos[0] += (pawn_width + 2)

    temp_pos = [x_display_size - (pawn_width + 2), start_y]
    for pawn in range(graphic_data.size):
        if (temp_pos[0] < (x_display_size - single_player_panel_x_size - 1)):
            temp_pos[1] += pawn_height + 1
            temp_pos[0] = x_display_size - (pawn_width + 2)
        dict_pawn["pawn_player2"].append((temp_pos[0], temp_pos[1]))
        temp_pos[0] -= (pawn_width + 2)

    display_dict = {}

    board_items = graphic_data.board_data.keys()
    for item in board_items:
        _ = []
        for position in graphic_data.board_data[item]:
            _.append((position[0] + (single_player_panel_x_size - 1), position[1]))
        display_dict[item] = _

    pawn_items = dict_pawn.keys()
    for item in pawn_items:
        display_dict[item] = dict_pawn[item]

    return_list = create_display_list((x_display_size, board_height))

    print_miltiple_items(graphic_data.graphics_data, display_dict, return_list)

    print_item_in_coordinates(["Player 1", " pawns: "], (0, start_y-3), return_list)
    print_item_in_coordinates(["Player 2", " pawns: "], (headline_x, start_y-3), return_list)

    return return_list, dict_pawn


class Display:
    def __init__(self, board: Board):
        self._board = board
        self._graphic_data = GraphicData(board.size)
        self._display_list, self._pawns_locations = create_full_display_list(self._graphic_data)

    def __str__(self):
        return_str = ''
        for row in self._display_list:
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
