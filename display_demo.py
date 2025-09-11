import time

from data_loaders import game_object_registry as gor
from data_loaders.game_data_loader import load_game_objects
from data_loaders.game_object_registry import all_game_objects_generator
from utils.display import CursesDisplay
from game_objects import (pawn, board, edge, field)
from game_objects.game_lord import GameLord
from game_objects.player import Player
from utils.display import CursesDisplay


def main():
    display = None

    try:
        load_game_objects(3)

        p1 = Player(1, {"up": ord("w"), "down": ord("s"), "left": ord("a"), "right": ord("d"), "interact": ord("e")})
        p2 = Player(2, {"up": ord("i"), "down": ord("k"), "left": ord("j"), "right": ord("l"), "interact": ord("o")})

        display = CursesDisplay(tuple(gor._BOARD_SIZE), 50)

        game_lord = GameLord._instance
        game_lord.display = display

        tasks = [
            display._render_process(all_game_objects_generator),
            p1.controll_procces(game_lord.pawn_interact_function, game_lord.cursor_move_function, game_lord.quit_function(display), display.input_key_pass),
            p2.controll_procces(game_lord.pawn_interact_function, game_lord.cursor_move_function, game_lord.quit_function(display), display.input_key_pass)
        ]

        while display.running:
            for task in tasks:
                task()
            game_lord.display.reset_key()

    except Exception as e:
        display._close_curses()
        raise e

    except KeyboardInterrupt:
        pass

    display._close_curses()


if __name__ == "__main__":
    main()
