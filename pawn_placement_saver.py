class PawnPlacementSaver:
    """
    A class that saves and manages pawn placements.

    Attributes:
        _depth (int): The maximum number of placements to be saved.
        _saved_placements (list): A list of saved placements.
        _mill_counter (int): The counter for mills occurred.
    """

    def __init__(self, depth: int):
        """
        Initializes a PawnPlacementSaver object.

        Args:
            depth (int): The maximum number of placements to be saved.
        """
        self._depth = depth
        self._saved_placements = []
        self._mill_counter = 0

    def save_placement(self, placement: list):
        """
        Saves a pawn placement.

        If the number of saved placements exceeds the maximum depth,
        the oldest placement will be removed.

        Args:
            placement (list): The pawn placement to be saved.
        """
        if len(self._saved_placements) >= self._depth:
            self._saved_placements.remove(self._saved_placements[0])
        self._saved_placements.append(placement)

    def check_if_repeated(self, placement: list):
        """
        Checks if a pawn placement is repeated.

        Args:
            placement (list): The pawn placement to be checked.

        Returns:
            int: The number of times the placement is repeated.
        """
        return self._saved_placements.count(placement)

    def mill_occurred(self):
        """
        Resets the mill counter.
        """
        self._mill_counter = 0

    def count_round_without_mill(self):
        """
        Increases the mill counter by 1.
        """
        self._mill_counter += 1

    @property
    def depth(self):
        """
        Gets the maximum depth of saved placements.

        Returns:
            int: The maximum depth.
        """
        return self._depth

    @property
    def mill_counter(self):
        """
        Gets the mill counter.

        Returns:
            int: The mill counter.
        """
        return self._mill_counter
