import curses


class Display:
    def __init__(self, size=(20, 10)):
        self.size = size
        self._init_colors()

    def _init_colors(self):
        curses.start_color()
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_WHITE)

    def get_drawable_bounds(self, wrapper, y, x, texture_width, texture_height):
        display_height, display_width = self.size
        terminal_height, terminal_width = wrapper.getmaxyx()

        effective_height = min(display_height, terminal_height)
        effective_width = min(display_width, terminal_width)

        y_end = max(min(texture_height, effective_height - y), 0)
        x_end = max(min(texture_width, effective_width - x), 0)

        return y_end, x_end

    def draw_basic_display(self, wrapper):
        height, width = wrapper.getmaxyx()

        if height >= self.size[1] + 1 and width >= self.size[0]:
            status_bar = "Display Ready"
            self.draw_status_bar(wrapper, status_bar)
            return True
        else:
            self._display_terminal_too_small_message(wrapper, height, width)
            return False

    def draw_colored_text(self, wrapper, y, x, text, color_pair):
        _, x_end = self.get_drawable_bounds(wrapper, y, x, len(text), 1)

        if x_end <= 0:
            return

        visible_text = text[:x_end]
        wrapper.attron(curses.color_pair(color_pair))
        wrapper.addstr(y, x, visible_text)
        wrapper.attroff(curses.color_pair(color_pair))

    def draw_status_bar(self, wrapper, text):
        height, width = wrapper.getmaxyx()
        if height < 1:
            return

        wrapper.attron(curses.color_pair(5))
        wrapper.attron(curses.A_BOLD)
        wrapper.addstr(height - 1, 0, text[: width - 1] if len(text) >= width else text)

        remaining = width - len(text) - 1
        if remaining > 0:
            wrapper.addstr(height - 1, len(text), " " * remaining)

        wrapper.attroff(curses.A_BOLD)
        wrapper.attroff(curses.color_pair(5))

    def draw_char(self, wrapper, y, x, char, color=1, bold=False):
        self.draw_element(wrapper, lambda: ((x, y), [char]), color, bold)

    def draw_element(self, wrapper, bound_render_func, color=1, bold=False):
        (y, x), texture = bound_render_func()
        texture_height = len(texture)
        texture_width = len(texture[0]) if texture_height > 0 else 0

        y_end, x_end = self.get_drawable_bounds(wrapper, y, x, texture_width, texture_height)

        if bold:
            wrapper.attron(curses.A_BOLD)
        wrapper.attron(curses.color_pair(color))

        for n, row in enumerate(texture[:y_end]):
            visible_row = row[:x_end]
            if visible_row:
                wrapper.addstr(y + n, x, visible_row)

        wrapper.attroff(curses.color_pair(color))
        if bold:
            wrapper.attroff(curses.A_BOLD)

    def _display_terminal_too_small_message(self, wrapper, height, width):
        x_message = width - self.size[0]
        y_message = height - (self.size[1] + 1)
        x_message = min(0, x_message)
        y_message = min(0, y_message)
        y_message = abs(y_message)

        message_01 = "board can't fit"
        message_02 = "expand the terminal"
        message_03 = f"by x:{abs(x_message)}, y:{y_message}"
        message_04 = "characters"

        start_x_message = int((width // 2) - (len(message_02) // 2) - len(message_02) % 2)
        start_y_message = int(height // 2)

        wrapper.attron(curses.color_pair(2))
        wrapper.attron(curses.A_BOLD)

        if height > 4:
            wrapper.addstr(start_y_message - 2, start_x_message, message_01)
            wrapper.addstr(start_y_message - 1, start_x_message, message_02)
            wrapper.addstr(start_y_message, start_x_message, message_03)
            wrapper.addstr(start_y_message + 1, start_x_message, message_04)
        else:
            wrapper.addstr(start_y_message, start_x_message, message_01)

        wrapper.attroff(curses.A_BOLD)
        wrapper.attroff(curses.color_pair(2))
