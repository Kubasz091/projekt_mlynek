from board import Board, Pawn, Dot
from graphic_data import GraphicData
import curses


class CoordinatesError(Exception):
    def __init__(self, text):
        super().__init__(self, text)


class Display:
    def __init__(self, size: int, game_lord):
        self._board = Board(size)
        self._graphic_data = GraphicData(size)
        self._display_list = []
        self._game_lord = game_lord

        self.create_full_display_list()

        curses.start_color()
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_WHITE)

    def pawn_str(self, pawn: Pawn):
        return list(self._graphic_data.graphics_data[f'pawn_player{int(not pawn.player_no_1)}'])

    def board_str(self):
        return_str = []
        for row in self._display_list:
            _ = ''
            for char in row:
                _ += char
            return_str.append(_)
        return return_str

    def create_display_list(self, size: tuple):
        return_list = []
        for row in range(size[1]):
            _ = []
            for char in range(size[0]):
                _.append(' ')
            return_list.append(_)
        return return_list

    def type_item_into_display_list(self, item: list, coordinates: tuple):
        if (coordinates[0] < 0 or coordinates[1] < 0):
            raise CoordinatesError("Coordinates cannot be negative!")
        if ((coordinates[0] + len(item[0])) > len(self._display_list[0])
           or (coordinates[1] + len(item)) > len(self._display_list)):
            raise CoordinatesError("Some part of the object outside of display bounds!")
        temp_pos = list(coordinates)
        for row in item:
            for char in row:
                if (char != " "):
                    self._display_list[temp_pos[1]][temp_pos[0]] = char
                temp_pos[0] += 1
            temp_pos[1] += 1
            temp_pos[0] = coordinates[0]

    def type_miltiple_items(self, items_with_positions: dict):
        indv_items_to_print = list(items_with_positions.keys())
        for item in indv_items_to_print:
            for position in items_with_positions[item]:
                self.type_item_into_display_list(self._graphic_data.graphics_data[item], position)

    def create_full_display_list(self):
        board_height = self._graphic_data.board_data["dot"][-1][1] + 3
        board_width = self._graphic_data.board_data["dot"][2][0] + 6

        pawn_height = len(self._graphic_data.graphics_data["pawn_player1"])
        pawn_width = len(self._graphic_data.graphics_data["pawn_player1"][0])
        pawn_columns = (((pawn_height + 2) * self._graphic_data.size) // board_height)
        if ((((pawn_height + 2) * self._graphic_data.size) % board_height) != 0):
            pawn_columns += 1
        if (pawn_columns == 1):
            pawn_columns += 1

        single_player_panel_x_size = (pawn_width + 2) * pawn_columns
        x_display_size = board_width + (2 * single_player_panel_x_size) + 2

        no_of_pawns_in_a_column = (self._graphic_data.size // pawn_columns)
        if (self._graphic_data.size % pawn_columns) != 0:
            no_of_pawns_in_a_column += 1

        start_y = int((board_height - (no_of_pawns_in_a_column * (pawn_height + 1))) / 2) + 1
        headline_x = x_display_size - (pawn_columns * (pawn_width + 2))

        temp_pos = [0, start_y]
        for pawn in range(self._graphic_data.size):
            if (temp_pos[0] > (single_player_panel_x_size - 1)):
                temp_pos[1] += pawn_height + 1
                temp_pos[0] = 0
            self._game_lord.add_player1_pawn(Pawn(temp_pos, True))
            temp_pos[0] += (pawn_width + 2)

        temp_pos = [x_display_size - (pawn_width+2), start_y]
        for pawn in range(self._graphic_data.size):
            if (temp_pos[0] < (x_display_size - single_player_panel_x_size - 1)):
                temp_pos[1] += pawn_height + 1
                temp_pos[0] = x_display_size - (pawn_width+2)
            self._game_lord.add_player2_pawn(Pawn(temp_pos, False))
            temp_pos[0] -= (pawn_width + 2)

        display_dict = {}
        board_items = list(self._graphic_data.board_data.keys())
        board_items.remove("connected_dots")
        for item in board_items:
            _ = []
            for position in self._graphic_data.board_data[item]:
                _.append((position[0] + (single_player_panel_x_size), position[1]))
            display_dict[item] = _

        for position in display_dict['dot']:
            self._game_lord.add_dot(Dot(list(position)))

        self._display_list = self.create_display_list((x_display_size, board_height))

        self.type_miltiple_items(display_dict)

        self.type_item_into_display_list(["Player 1", " pawns: "], (0, start_y-3))
        self.type_item_into_display_list(["Player 2", " pawns: "], (headline_x, start_y-3))

    def draw_display(self, wrapper):
        wrapper.clear()
        height, width = wrapper.getmaxyx()
        baord_str = self.board_str()

        if (height >= len(baord_str)+1 and width >= len(baord_str[0])):
            # keyboard functionality
            cursor_x, cursor_y = self._game_lord.keyboard_functionality(height, width)

            is_blue = self._game_lord.game_mechanics()

            statusbarstr = "Press 'q' to exit | Press 'e' to move pawns | Pos: {}, {}".format(int(cursor_x/2), cursor_y)

            i = 0
            for row in baord_str:
                wrapper.addstr(i, 0, row)
                i += 1
            del i

            # holding_pawn_text = "No pawn is currently being held"
            # if self._holding_pawn is not None:
            #     holding_pawn_text = f"{self._holding_pawn}"
            # whstr = "dot21 is connected with: dot{}, dot{}, dot{}".format(self._dots_list.index(self._dots_list[21]._dots_connected_with[0]), self._dots_list.index(self._dots_list[21]._dots_connected_with[1]), self._dots_list.index(self._dots_list[21]._dots_connected_with[2]))
            # wrapper.addstr(0, 1, whstr)

            for pawn in self._game_lord._player1_pawns:
                pawn_str = self.pawn_str(pawn)
                temp_pos = list(pawn.position)
                for row in pawn_str:
                    if (pawn.has_been_moved is True):
                        wrapper.attron(curses.color_pair(2))
                        wrapper.addstr(temp_pos[1], temp_pos[0], row)
                        wrapper.attroff(curses.color_pair(2))
                    else:
                        wrapper.addstr(temp_pos[1], temp_pos[0], row)
                    temp_pos[1] += 1
                del temp_pos

            for pawn in self._game_lord._player2_pawns:
                pawn_str = self.pawn_str(pawn)
                temp_pos = list(pawn.position)
                for row in pawn_str:
                    if (pawn.has_been_moved is True):
                        wrapper.attron(curses.color_pair(3))
                        wrapper.addstr(temp_pos[1], temp_pos[0], row)
                        wrapper.attroff(curses.color_pair(3))
                    else:
                        wrapper.addstr(temp_pos[1], temp_pos[0], row)
                    temp_pos[1] += 1
                del temp_pos

            # Render status bar
            wrapper.attron(curses.color_pair(5))
            wrapper.addstr(height-1, 0, statusbarstr)
            wrapper.addstr(height-1, len(statusbarstr), " " * (width - len(statusbarstr) - 1))
            wrapper.attroff(curses.color_pair(5))

            if (is_blue is True):
                wrapper.attron(curses.color_pair(1))
                wrapper.addstr(cursor_y, cursor_x, "██")
                wrapper.attroff(curses.color_pair(1))
            else:
                wrapper.attron(curses.color_pair(4))
                wrapper.addstr(cursor_y, cursor_x, "██")
                wrapper.attroff(curses.color_pair(4))

            # Refresh the screen and move the cursor for rendering so it is not next to my pointer
            wrapper.move(height - 1, width - 1)
            wrapper.refresh()

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

            wrapper.attron(curses.color_pair(2))
            wrapper.attron(curses.A_BOLD)

            if height > 4:
                wrapper.addstr(start_y_message-2, start_x_message, message_01)
                wrapper.addstr(start_y_message-1, start_x_message, message_02)
                wrapper.addstr(start_y_message, start_x_message, message_03)
                wrapper.addstr(start_y_message+1, start_x_message, message_04)
            else:
                wrapper.addstr(start_y_message, start_x_message, message_01)
            wrapper.attroff(curses.A_BOLD)
            wrapper.attroff(curses.color_pair(2))

            wrapper.move(height - 1, width - 1)

            wrapper.refresh()
