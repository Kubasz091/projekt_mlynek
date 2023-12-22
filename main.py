from display import Display
import curses
from time import sleep


def main(wrapper):
    display = Display(12)
    wrapper.clear()
    wrapper.refresh()
    while (display.key != ord("q")):
        display.draw_display(wrapper)


if __name__ == "__main__":
    curses.wrapper(main)
