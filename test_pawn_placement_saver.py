from pawn_placement_saver import PawnPlacementSaver


def test_save_placement():
    saver = PawnPlacementSaver(2)
    saver.save_placement([1, 2, 3])
    saver.save_placement([4, 5, 6])
    assert saver._saved_placements == [[1, 2, 3], [4, 5, 6]]
    saver.save_placement([7, 8, 9])
    assert saver._saved_placements == [[4, 5, 6], [7, 8, 9]]


def test_check_if_repeated():
    saver = PawnPlacementSaver(2)
    saver.save_placement([1, 2, 3])
    saver.save_placement([1, 2, 3])
    assert saver.check_if_repeated([1, 2, 3]) == 2
    saver.save_placement([4, 5, 6])
    assert saver.check_if_repeated([4, 5, 6]) == 1
    assert saver.check_if_repeated([1, 2, 3]) == 1
    assert saver.check_if_repeated([7, 8, 9]) == 0


def test_mill_occurred():
    saver = PawnPlacementSaver(2)
    saver.mill_occurred()
    assert saver._mill_counter == 0


def test_count_round_without_mill():
    saver = PawnPlacementSaver(2)
    saver.count_round_without_mill()
    assert saver._mill_counter == 1
    saver.count_round_without_mill()
    assert saver._mill_counter == 2
