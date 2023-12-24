from display import Display
import curses
from time import sleep, time


def main(wrapper):
    display = Display(12)

    wrapper.nodelay(True)

    wrapper.clear()
    display.draw_display(wrapper)
    wrapper.refresh()

    while (display.key != "q"):
        try:
            key = wrapper.getkey()
            display.set_key(key)
            display.draw_display(wrapper)
        except curses.error:
            pass


if __name__ == "__main__":
    curses.wrapper(main)
