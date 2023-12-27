from random import getrandbits


class GameLord:
    def __init__(self):
        self._player1_turn = bool(getrandbits(1))

    def change_turn(self):
        self._player1_turn = not self._player1_turn

    @property
    def player1_turn(self):
        return self._player1_turn
