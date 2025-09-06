import time

from data_loaders import game_object_registry as gor
from data_loaders.game_object_registry import all_game_objects_generator
from data_loaders.objects_reader import load_game_objects
from data_loaders.texture_registry import load_textures
from utils.display import CursesDisplay
from game_objects import (pawn, board, cursor, edge, field)


def move_cursor(display):
    next_frame_time = 0.0
    no_moves = 0
    moving_right = True

    def do_action():
        nonlocal next_frame_time, no_moves, moving_right
        if time.perf_counter() >= next_frame_time:
            if no_moves < 25 and moving_right:
                display.cursor2.move_right()
                no_moves += 1
            elif no_moves > 0 and not moving_right:
                display.cursor2.move_left()
                no_moves -= 1

            if no_moves == 25:
                moving_right = False
            elif no_moves == 0:
                moving_right = True

            next_frame_time = time.perf_counter() + 1 / 100

    return do_action


def main():
    load_textures()

    display = None

    try:
        load_game_objects(12)
        display = CursesDisplay(tuple(gor._BOARD_SIZE), 50)

        tasks = [display._render_process(all_game_objects_generator), move_cursor(display)]

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
