from board import Board, Pawn
from graphic_data import GraphicData
from time import sleep
import curses


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


def type_item_into_list(item: list, coordinates: tuple, display_list: list):
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


def type_miltiple_items(graphics_dict: dict, items_with_positions: dict, return_list: list):
    indv_items_to_print = list(items_with_positions.keys())
    for item in indv_items_to_print:
        for position in items_with_positions[item]:
            type_item_into_list(graphics_dict[item], position, return_list)


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

    no_of_pawns_in_a_column = (graphic_data.size // pawn_columns)
    if (graphic_data.size % pawn_columns) != 0:
        no_of_pawns_in_a_column += 1

    start_y = int((board_height - (no_of_pawns_in_a_column * (pawn_height + 1))) / 2) + 1
    headline_x = x_display_size - (pawn_columns * (pawn_width + 2))

    player1_pawns = []
    player2_pawns = []

    temp_pos = [0, start_y]
    for pawn in range(graphic_data.size):
        if (temp_pos[0] > (single_player_panel_x_size - 1)):
            temp_pos[1] += pawn_height + 1
            temp_pos[0] = 0
        player1_pawns.append(Pawn(temp_pos, 1))
        temp_pos[0] += (pawn_width + 2)

    temp_pos = [x_display_size - (pawn_width + 2), start_y]
    for pawn in range(graphic_data.size):
        if (temp_pos[0] < (x_display_size - single_player_panel_x_size - 1)):
            temp_pos[1] += pawn_height + 1
            temp_pos[0] = x_display_size - (pawn_width + 2)
        player2_pawns.append(Pawn(temp_pos, 2))
        temp_pos[0] -= (pawn_width + 2)

    display_dict = {}

    board_items = graphic_data.board_data.keys()
    for item in board_items:
        _ = []
        for position in graphic_data.board_data[item]:
            _.append((position[0] + (single_player_panel_x_size - 1), position[1]))
        display_dict[item] = _

    return_list = create_display_list((x_display_size, board_height))

    type_miltiple_items(graphic_data.graphics_data, display_dict, return_list)

    type_item_into_list(["Player 1", " pawns: "], (0, start_y-3), return_list)
    type_item_into_list(["Player 2", " pawns: "], (headline_x, start_y-3), return_list)

    return return_list, player1_pawns, player2_pawns


class Display:
    def __init__(self, board: Board):
        self._board = board
        self._graphic_data = GraphicData(board.size)
        self._display_list, pawns1, pawns2 = create_full_display_list(self._graphic_data)
        self._player1_pawns = pawns1
        self._player2_pawns = pawns2

    def pawn_str(self, pawn: Pawn):
        return list(self._graphic_data.graphics_data[f'pawn_player{pawn.player_no}'])

    def print_pawns_position(self):
        for player in self._pawns:
            for pawn in player:
                print(pawn.position)

    def check_if_above_pawn(self, position: list):
        pawn_return = []
        for player in [self._player1_pawns, self._player2_pawns]:
            for pawn in player:
                pos_left_corner = pawn.position
                pos_right_corner = [pos_left_corner[0] + len(self._graphic_data.graphics_data[f'pawn_player{pawn.player_no}'][0]),
                                    pos_left_corner[1] + len(self._graphic_data.graphics_data[f'pawn_player{pawn.player_no}'])]
                if (position[0] >= pos_left_corner[0] and position[0] < pos_right_corner[0]
                   and position[1] >= pos_left_corner[1] and position[1] < pos_right_corner[1]):
                    pawn_return.append(pawn)
        if (len(pawn_return) != 0):
            return pawn_return[0]

    @property
    def display_list(self):
        return self._display_list

    @property
    def player1_pawn_list(self):
        return self._player1_pawns

    @property
    def player2_pawn_list(self):
        return self._player2_pawns

    def __str__(self):
        return_str = ''
        for row in self._display_list:
            _ = ''
            for char in row:
                _ += char
            _ += '\n'
            return_str += _
        return return_str


display = Display(Board(12))
baord_str = []
for row in display.display_list:
    _ = ''
    for char in row:
        _ += char
    baord_str.append(_)


def draw_display(stdscr):
    k = 0
    cursor_x = 0
    cursor_y = 0
    catch = False
    saved_pos = None
    position_difference = None
    holding_pawn = None

    stdscr.clear()
    stdscr.refresh()

    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_WHITE)

    # Loop where k is the last character pressed, and it updates the display when some key was pressed
    while (k != ord('q')):
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        if (height >= len(baord_str) and width >= len(baord_str[0])):

            # keyboard functionality
            if k == curses.KEY_DOWN:
                cursor_y = cursor_y + 1
            elif k == curses.KEY_UP:
                cursor_y = cursor_y - 1
            elif k == curses.KEY_RIGHT:
                cursor_x = cursor_x + 2
            elif k == curses.KEY_LEFT:
                cursor_x = cursor_x - 2
            elif k == ord('e'):
                catch = not catch
                if (saved_pos is not None):
                    holding_pawn.set_position(saved_pos)

            cursor_x = max(0, cursor_x)
            cursor_x = min(width-2, cursor_x)

            cursor_y = max(0, cursor_y)
            cursor_y = min(height-2, cursor_y)

            if catch is True and holding_pawn is not None:
                holding_pawn.set_position([cursor_x-position_difference[0], cursor_y-position_difference[1]])

            statusbarstr = "Press 'q' to exit | Press 'e' to move pawns | Pos: {}, {}".format(int(cursor_x/2), cursor_y)

            i = 0
            for row in baord_str:
                stdscr.addstr(i, 0, row)
                i += 1
            del i

            holding_pawn_text = "No pawn is currently being held"
            if holding_pawn is not None:
                holding_pawn_text = f"{holding_pawn}"
            whstr = "holding_pawn: {}".format(holding_pawn_text)
            stdscr.addstr(0, 1, whstr)

            stdscr.attron(curses.color_pair(2))
            for pawn in display.player1_pawn_list:
                pawn_str = display.pawn_str(pawn)
                temp_pos = list(pawn.position)
                for row in pawn_str:
                    stdscr.addstr(temp_pos[1], temp_pos[0], row)
                    temp_pos[1] += 1
                del temp_pos
            stdscr.attroff(curses.color_pair(2))

            stdscr.attron(curses.color_pair(3))
            for pawn in display.player2_pawn_list:
                pawn_str = display.pawn_str(pawn)
                temp_pos = list(pawn.position)
                for row in pawn_str:
                    stdscr.addstr(temp_pos[1], temp_pos[0], row)
                    temp_pos[1] += 1
                del temp_pos
            stdscr.attroff(curses.color_pair(3))

            # Render status bar
            stdscr.attron(curses.color_pair(5))
            stdscr.addstr(height-1, 0, statusbarstr)
            stdscr.addstr(height-1, len(statusbarstr), " " * (width - len(statusbarstr) - 1))
            stdscr.attroff(curses.color_pair(5))

            if (catch is False):
                stdscr.attron(curses.color_pair(1))
                stdscr.addstr(cursor_y, cursor_x, "██")
                stdscr.attroff(curses.color_pair(1))
                if holding_pawn is not None:
                    holding_pawn = None
                    saved_pos = None
                    position_difference = None
            elif (catch is True):
                stdscr.attron(curses.color_pair(4))
                stdscr.addstr(cursor_y, cursor_x, "██")
                stdscr.attroff(curses.color_pair(4))
                if holding_pawn is None:
                    holding_pawn = display.check_if_above_pawn([cursor_x, cursor_y])
                    if holding_pawn is None:
                        catch = not catch
                    elif (saved_pos is None):
                        saved_pos = list(holding_pawn.position)
                        position_difference = list([cursor_x-saved_pos[0], cursor_y-saved_pos[1]])

            # Refresh the screen and move the cursor for rendering so it is not next to my pointer
            stdscr.move(height - 1, width - 1)
            stdscr.refresh()

            sleep(0.02)
            if (catch is False and k == ord("e")):
                stdscr.attron(curses.color_pair(1))
                stdscr.addstr(cursor_y, cursor_x, "██")
                stdscr.attroff(curses.color_pair(1))
                stdscr.move(height - 1, width - 1)
                stdscr.refresh()

            # Wait for next input
            k = stdscr.getch()

        # if terminal size is not big enough to fit the whole board notify the user
        else:
            x_message = width - len(baord_str[0])
            y_message = height - len(baord_str)
            x_message = min(0, x_message)
            y_message = min(0, y_message)
            y_message = abs(y_message)

            message_01 = "board can't fit"
            message_02 = "expand the terminal"
            message_03 = f'by x:{x_message}, y:{y_message}'
            message_04 = "characters"

            start_x_message = int((width // 2) - (len(message_02) // 2) - len(message_02) % 2)
            start_y_message = int((height // 2))

            stdscr.attron(curses.color_pair(2))
            stdscr.attron(curses.A_BOLD)

            if height > 4:
                stdscr.addstr(start_y_message-2, start_x_message, message_01)
                stdscr.addstr(start_y_message-1, start_x_message, message_02)
                stdscr.addstr(start_y_message, start_x_message, message_03)
                stdscr.addstr(start_y_message+1, start_x_message, message_04)
            else:
                stdscr.addstr(start_y_message, start_x_message, message_01)
            stdscr.attroff(curses.A_BOLD)
            stdscr.attroff(curses.color_pair(2))

            stdscr.move(height - 1, width - 1)

            stdscr.refresh()
            sleep(0.02)
            k = stdscr.getch()

if __name__ == "__main__":
        curses.wrapper(draw_display)
