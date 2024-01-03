class PawnPlacementSaver:
    def __init__(self, depth: int):
        self._depth = depth
        self._saved_placements = []
        self._mill_counter = 0

    def save_placement(self, placement: list):
        if len(self._saved_placements) >= self._depth:
            self._saved_placements.remove(self._saved_placements[0])
        self._saved_placements.append(placement)

    def check_if_repeted(self, placement: list):
        return self._saved_placements.count(placement)

    def mill_occured(self):
        self._mill_counter = 0

    def count_round_without_mill(self):
        self._mill_counter += 1

    @property
    def depth(self):
        return self._depth

    @property
    def mill_counter(self):
        return self._mill_counter
