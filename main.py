import curses
from time import sleep, time
from game_lord import GameLord


class ProgramRunner:
    def __init__(self):
        chose_size = False
        self._size = 0
        self._bot = False

        while chose_size is False:
            self._size = int(input("Choose ammount of pawns that each player will have (3, 6, 9, 12) --> "))
            if self._size in [3, 6, 9, 12]:
                chose_size = True
            else:
                print("Typed in wrong size :(")

        chose_bot = False
        while chose_bot is False:
            typein = int(input("if you want to play against a bot, type in 1 if not type in 0 --> "))
            if typein in [0, 1]:
                chose_bot = True
                self._bot = bool(typein)
            else:
                print("Typed in something, that's not 0 or 1 :(")

    def run(self, wrapper):
        game_lord = GameLord(self._size)

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
    program_runner = ProgramRunner()
    curses.wrapper(program_runner.run)
