from display import Display
import curses
from time import sleep, time
from game_lord import GameLord


def main(wrapper):
    game_lord = GameLord()
    display = Display(12, game_lord)

    wrapper.nodelay(True)

    wrapper.clear()
    display.draw_display(wrapper)
    wrapper.refresh()

    time_started = time()
    time_to_display = 0

    while (display.key != "q"):
        try:
            current_time = time() - time_started
            if (current_time > time_to_display):
                key = wrapper.getkey()
                display.set_key(key)
                display.draw_display(wrapper)
                time_to_display = current_time + 0.02
        except curses.error:
            pass


if __name__ == "__main__":
    curses.wrapper(main)
