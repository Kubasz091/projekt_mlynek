from board import Board, Pawn, Dot
from graphic_data import GraphicData
import curses
from time import sleep


class CoordinatesError(Exception):
    def __init__(self, text):
        super().__init__(self, text)


class Display:
    def __init__(self, size: int, game_lord):
        self._board = Board(size)
        self._graphic_data = GraphicData(size)
        self._display_list = []
        self._game_lord = game_lord
        self._headline_y = None
        self._headline_x = None

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
        board_height = self._graphic_data.board_data["dot"][-1][1] + 3 + 4
        board_width = self._graphic_data.board_data["dot"][2][0] + 6

        pawn_height = len(self._graphic_data.graphics_data["pawn_player1"])
        pawn_width = len(self._graphic_data.graphics_data["pawn_player1"][0])
        pawn_columns = (((pawn_height + 2) * self._graphic_data.size) // board_height)
        if ((((pawn_height + 2) * self._graphic_data.size) % board_height) != 0):
            pawn_columns += 1
        if (pawn_columns == 1):
            pawn_columns += 1

        single_player_panel_x_size = ((pawn_width + 2) * pawn_columns) + 4
        x_display_size = board_width + (2 * single_player_panel_x_size)

        no_of_pawns_in_a_column = (self._graphic_data.size // pawn_columns)
        if (self._graphic_data.size % pawn_columns) != 0:
            no_of_pawns_in_a_column += 1

        self._headline_y = int((board_height - (no_of_pawns_in_a_column * (pawn_height + 1))) / 2)+2
        self._headline_x = x_display_size - (pawn_columns * (pawn_width + 2) + 4)+2

        temp_pos = [4, self._headline_y]
        for pawn in range(self._graphic_data.size):
            if (temp_pos[0] > (single_player_panel_x_size-1)):
                temp_pos[1] += pawn_height + 1
                temp_pos[0] = 4
            self._game_lord.add_player1_pawn(Pawn(temp_pos, True))
            temp_pos[0] += (pawn_width + 2)

        temp_pos = [x_display_size - (pawn_width+2+2), self._headline_y]
        for pawn in range(self._graphic_data.size):
            if (temp_pos[0] < (x_display_size - single_player_panel_x_size-1)):
                temp_pos[1] += pawn_height + 1
                temp_pos[0] = x_display_size - (pawn_width+2+2)
            self._game_lord.add_player2_pawn(Pawn(temp_pos, False))
            temp_pos[0] -= (pawn_width + 2)

        display_dict = {}
        board_items = list(self._graphic_data.board_data.keys())
        board_items.remove("connected_dots")
        for item in board_items:
            _ = []
            for position in self._graphic_data.board_data[item]:
                _.append((position[0] + (single_player_panel_x_size), position[1] + 2))
            display_dict[item] = _

        for position in display_dict['dot']:
            self._game_lord.add_dot(Dot(list(position)))

        self._display_list = self.create_display_list((x_display_size, board_height))

        self.type_miltiple_items(display_dict)

    def draw_display(self, wrapper):
        wrapper.clear()
        height, width = wrapper.getmaxyx()
        baord_str = self.board_str()

        if (height >= len(baord_str)+1 and width >= len(baord_str[0]) and self._game_lord._player1_won is False
           and self._game_lord._player2_won is False and self._game_lord._draw is False):

            cursor_x, cursor_y = self._game_lord.keyboard_functionality(len(baord_str)+1, len(baord_str[0]))

            is_off = self._game_lord.game_mechanics()

            if self._game_lord.player1_turn is True:
                player_str = 'PLAYER 1 TURN'
            else:
                player_str = 'PLAYER 2 TURN'
            statusbarstr = "Press 'q' to exit | Press 'e' to move pawns | Pos: {}, {},   {}".format(int(cursor_x/2), cursor_y, player_str)

            i = 0
            for row in baord_str:
                wrapper.addstr(i, 0, row)
                i += 1
            del i

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

            wrapper.attron(curses.color_pair(5))
            wrapper.addstr(height-1, 0, statusbarstr)
            wrapper.addstr(height-1, len(statusbarstr), " " * (width - len(statusbarstr) - 1))
            wrapper.attroff(curses.color_pair(5))

            wrapper.attron(curses.A_BOLD)
            wrapper.attron(curses.color_pair(2))
            wrapper.addstr(self._headline_y-3, 4, "Player 1")
            wrapper.addstr(self._headline_y-2, 4, " pawns: ")
            wrapper.attroff(curses.color_pair(2))

            wrapper.attron(curses.color_pair(3))
            wrapper.addstr(self._headline_y-3, self._headline_x, "Player 2")
            wrapper.addstr(self._headline_y-2, self._headline_x, " pawns: ")
            wrapper.attroff(curses.color_pair(3))
            wrapper.attroff(curses.A_BOLD)

            if (is_off is True):
                if self._game_lord.player1_turn is True:
                    wrapper.attron(curses.color_pair(2))
                    wrapper.addstr(cursor_y, cursor_x, "██")
                    wrapper.attroff(curses.color_pair(2))
                else:
                    wrapper.attron(curses.color_pair(3))
                    wrapper.addstr(cursor_y, cursor_x, "██")
                    wrapper.attroff(curses.color_pair(3))
            else:
                wrapper.attron(curses.color_pair(4))
                wrapper.addstr(cursor_y, cursor_x, "██")
                wrapper.attroff(curses.color_pair(4))

            wrapper.move(height - 1, width - 1)
            wrapper.refresh()

        # if terminal size is not big enough to fit the whole board notify the user
        elif (height < len(baord_str)+1 and width < len(baord_str[0]) and self._game_lord._player1_won is False
              and self._game_lord._player2_won is False and self._game_lord._draw is False):
            x_message = width - len(baord_str[0])
            y_message = height - (len(baord_str)+1)
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
        elif self._game_lord._player1_won is True:
            start_x = int((width - len(self._graphic_data.graphics_data['player1_won'][0]))/2)
            start_y = int((height - len(self._graphic_data.graphics_data['player1_won']))/2)
            i = 0
            for row in self._graphic_data.graphics_data['player1_won']:
                wrapper.addstr(start_y + i, start_x, row)
                i += 1
            wrapper.move(height - 1, width - 1)
            wrapper.refresh()
            sleep(5)
            exit()

        elif self._game_lord._player2_won is True:
            start_x = int((width - len(self._graphic_data.graphics_data['player2_won'][0]))/2)
            start_y = int((height - len(self._graphic_data.graphics_data['player2_won']))/2)
            i = 0
            for row in self._graphic_data.graphics_data['player2_won']:
                wrapper.addstr(start_y + i, start_x, row)
                i += 1
            wrapper.move(height - 1, width - 1)
            wrapper.refresh()
            sleep(5)
            exit()
        elif self._game_lord._draw is True:
            start_x = int((width - len(self._graphic_data.graphics_data['draw'][0]))/2)
            start_y = int((height - len(self._graphic_data.graphics_data['draw']))/2)
            i = 0
            for row in self._graphic_data.graphics_data['draw']:
                wrapper.addstr(start_y + i, start_x, row)
                i += 1
            wrapper.move(height - 1, width - 1)
            wrapper.refresh()
            sleep(5)
            exit()
