import curses
import time
from abc import ABC, abstractmethod
from typing import Callable

from data_loaders.terminal_texture import Texture
from game_objects.cursor import Cursor


class Display(ABC):
    def __init__(self, size=(20, 10), goal_Hz=50.0):
        self.size = size
        self.output = None
        self._goal_refresh_time = 1 / goal_Hz

    @abstractmethod
    def render_frame(self, gen_objs_to_render=None):
        pass


class CursesDisplay(Display):  # renders only terminal textures
    def __init__(self, size=(20, 10), goal_Hz=50.0):
        super().__init__(size, goal_Hz)

        self._current_key_pressed = -1
        self._current_size_y = 0
        self._current_size_x = 0

        self.statusbar_text = "Press 'q' to exit | 'e' to move pawns | '←↑→↓' to Move"

        self.cursor1 = Cursor(
            size,
            texture={"name": "cursorP1"},
            id=1,
            position={"y": 0, "x": 8},
            hitbox_size=(3, 4),
            hitbox_position=(-1, -1),
            connections={
                "PawnP1": {
                    "class_name": "Cursor",
                    "connector_data": {
                        1: {
                            "position": {"y": 0, "x": 0},
                            "id": 1,
                            "allign_offset": 1,
                            "hitbox_position": (-1, -1),
                            "hitbox_size": (3, 4),
                            "obj": None,
                        }
                    },
                }
            },
        )
        self.cursor2 = Cursor(
            size,
            texture={"name": "cursorP2"},
            id=2,
            position={"y": 12, "x": 0},
            hitbox_size=(3, 4),
            hitbox_position=(-1, -1),
            connections={
                "PawnP2": {
                    "class_name": "Cursor",
                    "connector_data": {
                        1: {
                            "position": {"y": 0, "x": 0},
                            "id": 1,
                            "allign_offset": 1,
                            "hitbox_position": (-1, -1),
                            "hitbox_size": (3, 4),
                            "obj": None,
                        }
                    },
                }
            },
        )

        self._init_curses()

        self.running = True

    def _render_process(self, gen_objs_acces_func=None):
        _curr_time = time.perf_counter()
        _next_frame = 0.0

        def do_render():
            nonlocal _curr_time, _next_frame

            _curr_time = time.perf_counter()
            if self.running and (_curr_time >= _next_frame):
                self._input_procces()
                self.render_frame(gen_objs_acces_func)

                _next_frame = _curr_time + self._goal_refresh_time

        return do_render

    def _input_procces(self):
        key = self._get_curr_key()

        if key == ord("q"):
            self.running = False
        elif key == curses.KEY_UP:
            self.cursor2.move_up()
        elif key == curses.KEY_DOWN:
            self.cursor2.move_down()
        elif key == curses.KEY_LEFT:
            self.cursor2.move_left()
        elif key == curses.KEY_RIGHT:
            self.cursor2.move_right()

    def input_key_pass(self):
        return self._current_key_pressed

    def render_frame(self, gen_objs_acces_func=None):
        self.output.clear()

        if self._draw_basic_display() and gen_objs_acces_func:
            for obj in gen_objs_acces_func():
                self.draw_texture(obj.render)

            self.draw_texture(self.cursor1.render)
            self.draw_texture(self.cursor2.render)

        self.output.refresh()

    def draw_texture(self, bound_render_func: Callable[[], tuple[tuple[int, int], Texture]]):
        (y, x), texture = bound_render_func()

        if texture is None:
            return

        y_end, x_end = self._get_drawable_bounds(y, x, texture.width, texture.height)

        if texture.bold:
            self.output.attron(curses.A_BOLD)
        if texture.color:
            self.output.attron(curses.color_pair(texture.color))

        for n, row in enumerate(texture[:y_end]):
            visible_row = row[:x_end]
            if visible_row:
                self.output.addstr(y + n, x, visible_row)

        if texture.color:
            self.output.attroff(curses.color_pair(texture.color))
        if texture.bold:
            self.output.attroff(curses.A_BOLD)

    def _draw_status_bar(self, text=None):
        if self._current_size_y < 1:
            return

        if not text:
            text = self.statusbar_text + f" cursor1 pos {self.cursor1.position}"

        remaining = self._current_size_x - len(text) - 1
        fill_spaces = " " * max(0, remaining)

        text = text + fill_spaces

        self.output.attron(curses.color_pair(5))
        self.output.addstr(self._current_size_y - 1, 0, text[: self._current_size_x])
        self.output.attroff(curses.color_pair(5))

    #
    #
    #

    def _get_curr_key(self):
        try:
            self._current_key_pressed = self.output.getch()
        except Exception:
            self._current_key_pressed = -1
        return self._current_key_pressed

    def _get_drawable_bounds(self, y, x, texture_width, texture_height):
        display_height, display_width = self.size

        effective_height = min(display_height, self._current_size_y)
        effective_width = min(display_width, self._current_size_x)

        y_end = max(min(texture_height, effective_height - y), 0)
        x_end = max(min(texture_width, effective_width - x), 0)

        return y_end, x_end

    def _draw_basic_display(self):  # and handle too small terminal size for the display
        self._current_size_y, self._current_size_x = self.output.getmaxyx()

        if self._current_size_y >= self.size[0] + 1 and self._current_size_x >= self.size[1]:
            self._draw_status_bar()
            return True
        else:
            self._display_terminal_too_small_message()
            return False

    def _display_terminal_too_small_message(self):
        _x_message = abs(min(0, self._current_size_x - self.size[1]))
        _y_message = abs(min(0, self._current_size_y - (self.size[0] + 1)))

        _message = (
            "board can't fit",
            "expand the terminal",
            f"by x:{_x_message}, y:{_y_message}",
            "characters",
        )
        _max_len = max(len(msg) for msg in _message)

        start_x_message = int((min(self.size[1], self._current_size_x) // 2) - (_max_len // 2) - _max_len % 2)
        start_y_message = int(min(self.size[0], self._current_size_y // 2)) - 2

        self.output.attron(curses.color_pair(2))
        self.output.attron(curses.A_BOLD)

        if self._current_size_x > 4:
            for line in _message:
                self.output.addstr(start_y_message, start_x_message, line[: self._current_size_x])
        else:
            self.output.addstr(start_y_message, start_x_message, _message[0][: self._current_size_x])

        self.output.attroff(curses.A_BOLD)
        self.output.attroff(curses.color_pair(2))

    def _init_curses(self):
        self.output = curses.initscr()

        curses.curs_set(0)
        curses.noecho()
        curses.cbreak()

        self.output.keypad(True)
        self.output.nodelay(True)

        curses.start_color()
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_WHITE)

    def _close_curses(self):
        self.output.keypad(False)
        curses.echo()
        curses.nocbreak()
        curses.endwin()
