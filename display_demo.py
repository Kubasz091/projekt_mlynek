import time

from data_loaders import game_object_registry as gor
from data_loaders.game_data_loader import load_game_objects
from data_loaders.game_object_registry import all_game_objects_generator
from utils.display import CursesDisplay
from game_objects import (pawn, board, edge, field)
from game_objects.game_lord import GameLord
from game_objects.player import Player
from utils.display import CursesDisplay


def move_cursor(cursor):
    next_frame_time = 0.0
    no_moves = 0
    moving_right = True

    def do_action():
        nonlocal next_frame_time, no_moves, moving_right
        if time.perf_counter() >= next_frame_time:
            if no_moves < 25 and moving_right:
                cursor.move_right()
                no_moves += 1
            elif no_moves > 0 and not moving_right:
                cursor.move_left()
                no_moves -= 1

            if no_moves == 25:
                moving_right = False
            elif no_moves == 0:
                moving_right = True

            next_frame_time = time.perf_counter() + 1 / 100

    return do_action


def main():
    display = None

    try:
        load_game_objects(12)

        p1 = Player(2, {"up": ord("w"), "down": ord("s"), "left": ord("a"), "right": ord("d"), "interact": ord("e")})
        display = CursesDisplay(tuple(gor._BOARD_SIZE), 50)
        game_lord = GameLord._instance

        tasks = [display._render_process(all_game_objects_generator), move_cursor(gor.resolve_game_object("Cursor", 1)), p1.controll_procces(game_lord.pawn_interact_function, game_lord.cursor_move_function, game_lord.quit_function(display), display.input_key_pass)]

        while display.running:
            for task in tasks:
                task()

    except Exception as e:
        display._close_curses()
        raise e

    except KeyboardInterrupt:
        pass

    display._close_curses()


if __name__ == "__main__":
    main()
