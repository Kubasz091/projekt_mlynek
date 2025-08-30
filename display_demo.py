import threading
import time

from data_loaders.game_object_registry import all_game_objects_generator
from data_loaders.objects_reader import load_game_objects
from game_objects.display import CursesDisplay


def worker(display: CursesDisplay):
    display.ui_ready.wait()

    with display.state_lock:
        display.cursor1.move_down()

    for _ in range(5):
        time.sleep(0.2)
        with display.state_lock:
            display.cursor1.move_down()


def main():
    display = CursesDisplay((90, 90), 50)

    load_game_objects(3)

    threading.Thread(target=worker, daemon=True, args=(display,)).start()

    display.run(gen_objs_acces_func=all_game_objects_generator)


if __name__ == "__main__":
    main()
