import curses
from time import sleep, time
from game_lord import GameLord


def main(wrapper):
    game_lord = GameLord(3)

    wrapper.nodelay(True)

    wrapper.clear()
    game_lord.display_frame(wrapper)
    wrapper.refresh()

    time_started = time()
    time_to_display = 0

    while (game_lord.key != "q"):
        current_time = time() - time_started

        if (current_time > time_to_display):
            key = None
            try:
                key = wrapper.getkey()
            except Exception:
                pass
            game_lord.set_key(key)
            if (key is not None):
                game_lord.display_frame(wrapper)
                time_to_display = current_time + 0.02
            elif (game_lord.one_more_frame is True):
                game_lord.display_frame(wrapper)
                time_to_display = current_time + 0.02
                game_lord.displayed_one_more_frame()

if __name__ == "__main__":
    curses.wrapper(main)
