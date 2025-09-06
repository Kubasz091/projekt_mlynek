from game_objects.game_object import GameObject


class Cursor(GameObject):  # make it able to move the pawns around
    def __init__(self, bounds: tuple[int, int], **kwargs):
        super().__init__(**kwargs)

        self.bounds = (bounds[0] - 1, bounds[1] - 1)

    def move_up(self):
        if self.position[0] >= 1:
            self.position[0] -= 1

    def move_down(self):
        if self.position[0] <= self.bounds[0] - 1:
            self.position[0] += 1

    def move_left(self):
        if self.position[1] >= 2:
            self.position[1] -= 2

    def move_right(self):
        if self.position[1] <= self.bounds[1] - 2:
            self.position[1] += 2
