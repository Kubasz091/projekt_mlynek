from game_objects.game_object import Connectable, GameObject
from game_objects.pawn import Pawn


class Cursor(GameObject, Connectable):
    def __init__(self, bounds: tuple[int, int], **kwargs):
        super().__init__(**kwargs)

        self._normal_color = self.texture.color
        self._click_color = 4

        self._pawn_connection_name = "PawnP" + str(self.id)
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

    def click(self):
        if self.texture.color == self._normal_color:
            self.texture.color = self._click_color
        else:
            self.texture.color = self._normal_color

    @property
    def pawn(self):
        return self.connections[self._pawn_connection_name][1]

    @pawn.setter
    def pawn(self, value):
        if value is None:
            self.connections[self._pawn_connection_name]._dict[1].obj = None
        elif isinstance(value, Pawn):
            self.connections[self._pawn_connection_name]._dict[1].obj = value

    @property
    def hitbox(self):
        return self.connector_hitboxes[self._pawn_connection_name].hitbox_array
