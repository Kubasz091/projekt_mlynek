import curses
import time

from data_loaders.terminal_texture import Texture
from game_objects.cursor import Cursor
from game_objects.display import Display


def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(1)

    display = Display((40, 20))

    cursor_texture = Texture(["a██a"])

    cursor = Cursor((5, 10), cursor_texture, (40, 20), 0)

    cursor_color = 4

    running = True
    frame = 0
    status_message = "Welcome to Display Demo"

    while running:
        stdscr.clear()
        draw_more = display.draw_basic_display(stdscr)
        if draw_more:
            height, width = stdscr.getmaxyx()

            title = "Interactive Display Demo"
            display.draw_colored_text(stdscr, 1, (width - len(title)) // 2, title, 1)

            instructions = [
                "← → ↑ ↓ : Move cursor",
                "c: Change cursor color",
                "q: Quit",
            ]

            for i, instruction in enumerate(instructions):
                display.draw_colored_text(stdscr, i + 3, 2, instruction, 3)

            display.draw_element(stdscr, cursor.render, cursor_color)

            display.draw_status_bar(stdscr, status_message)

            stdscr.refresh()
            try:
                key = stdscr.getch()
            except Exception:
                key = -1

            if key == ord("q"):
                running = False
            elif key == curses.KEY_UP and cursor.position[0] > 0:
                cursor.move((cursor.position[0] - 1, cursor.position[1]))
                status_message = f"Cursor position: y={cursor.position[0]}, x={cursor.position[1]}"
            elif key == curses.KEY_DOWN and cursor.position[0] < height - 2:
                cursor.move((cursor.position[0] + 1, cursor.position[1]))
                status_message = f"Cursor position: y={cursor.position[0]}, x={cursor.position[1]}"
            elif key == curses.KEY_LEFT and cursor.position[1] > 0:
                cursor.move((cursor.position[0], cursor.position[1] - 1))
                status_message = f"Cursor position: y={cursor.position[0]}, x={cursor.position[1]}"
            elif key == curses.KEY_RIGHT and cursor.position[1] < width - 2:
                cursor.move((cursor.position[0], cursor.position[1] + 1))
                status_message = f"Cursor position: y={cursor.position[0]}, x={cursor.position[1]}"
            elif key == ord("c"):
                cursor_color = (cursor_color % 4) + 1
                color_names = {1: "Cyan", 2: "Red", 3: "Green", 4: "Yellow"}
                status_message = f"Cursor color: {color_names[cursor_color]}"

            frame += 1
        else:
            stdscr.refresh()

        time.sleep(0.03)


if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass
