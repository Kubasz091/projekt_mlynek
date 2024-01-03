import curses
from time import time
from game_lord import GameLord


class ProgramRunner:
    """
    Class responsible for running the program and managing the game settings.

    Attributes:
        _size (int): The number of pawns that each player will have.
        _bot (bool): Indicates whether the player is playing against a bot or not.
        _bot_mode (bool): The bot operation mode (random moves or simple logical moves).

    Methods:
        __init__(): Initializes the ProgramRunner object and prompts the user to choose game settings.
        run(wrapper): Runs the game loop and displays the game frame.
    """

    def __init__(self):
        chose_size = False
        self._size = 0
        self._bot = False
        self._bot_mode = None

        while chose_size is False:
            try:
                self._size = int(input("Choose amount of pawns that each player will have (3, 6, 9, 12) --> "))
            except Exception:
                self._size = 5
            if self._size in [3, 6, 9, 12]:
                chose_size = True
            else:
                print("Typed in something that's not 3, 6, 9, or 12 :(")

        chose_bot = False
        while chose_bot is False:
            try:
                typein = int(input("If you want to play against a bot, type in 1. If not, type in 0 --> "))
            except Exception:
                typein = 2
            if typein in [0, 1]:
                chose_bot = True
                self._bot = bool(typein)
            else:
                print("Typed in something that's not 0 or 1 :(")

        if self._bot is True:
            chose_bot_mode = False
            while chose_bot_mode is False:
                try:
                    typein = int(input("Choose bot operation mode (1 for random moves, 0 for simple logical moves) --> "))
                except Exception:
                    typein = 2
                if typein in [0, 1]:
                    chose_bot_mode = True
                    self._bot_mode = bool(typein)
                else:
                    print("Typed in something that's not 0 or 1 :(")

    def run(self, wrapper):
        """
        Runs the game loop and displays the game frame.

        Args:
            wrapper: The wrapper object used for displaying the game frame.

        Returns:
            None
        """
        self._game_lord = GameLord(self._size, self._bot, self._bot_mode)
        wrapper.nodelay(True)

        wrapper.clear()
        self._game_lord.display_frame(wrapper)
        wrapper.refresh()

        time_started = time()
        time_to_display = 0

        while self._game_lord.key != "q":
            current_time = time() - time_started

            if current_time > time_to_display:
                key = None
                try:
                    key = wrapper.getkey()
                except Exception:
                    pass
                self._game_lord.set_key(key)
                if key is not None:
                    self._game_lord.display_frame(wrapper)
                    time_to_display = current_time + 0.02
                elif self._game_lord.one_more_frame > 0:
                    self._game_lord.display_frame(wrapper)
                    time_to_display = current_time + 0.02
                    self._game_lord.displayed_one_more_frame()


if __name__ == "__main__":
    program_runner = ProgramRunner()
    curses.wrapper(program_runner.run)
