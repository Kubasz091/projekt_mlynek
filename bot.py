class Bot:
    def __init__(self, random_moves: bool):
        self._random_moves = random_moves

    @property
    def random(self):
        return self._random_moves
