import importlib
import os
import sys

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Import after path fix without violating E402
FullCoverageMap = importlib.import_module("game_objects.hitboxes").FullCoverageMap


def test_register_and_complete_noncontiguous_mill():
    mh = FullCoverageMap(8, 12)
    mid = 777
    pts = [(1, 1), (1, 5), (1, 9)]
    mh.register_mill(pts, mid)

    # All required cells occupied
    pawns = np.zeros_like(mh.hitbox_array, dtype=np.uint16)
    for y, x in pts:
        pawns[y, x] = 1

    completed, cnt = mh.check_completed_mills(pawns)
    assert mid in completed
    assert cnt >= 1


def test_incomplete_mill_not_completed():
    mh = FullCoverageMap(8, 12)
    mid = 42
    pts = [(2, 2), (2, 6), (2, 10)]
    mh.register_mill(pts, mid)

    # Leave one missing
    pawns = np.zeros_like(mh.hitbox_array, dtype=np.uint16)
    pawns[2, 2] = 1
    pawns[2, 6] = 1

    completed, cnt = mh.check_completed_mills(pawns)
    assert mid not in completed
    assert cnt == 0


def test_update_mill_balances_overlap_and_preserves_existing():
    mh = FullCoverageMap(10, 10)

    arrA = np.zeros((2, 4), dtype=np.uint16)
    arrA[:] = 101
    arrB = np.zeros((2, 4), dtype=np.uint16)
    arrB[:] = 202

    mh.update_mill((4, 3), arrA)
    # Ensure A is present
    subA = mh.hitbox_array[4:6, 3:7]
    assert np.any(subA == 101)

    # Overlap with B
    mh.update_mill((4, 4), arrB)
    sub = mh.hitbox_array[4:6, 3:8]

    # Check preservation: A still present in the region
    assert np.any(sub == 101)

    # Check balancing: counts within +/-1 where both ids exist
    vals = sub[sub != 0]
    ids, counts = np.unique(vals, return_counts=True)
    if len(ids) >= 2:
        assert abs(int(counts.max()) - int(counts.min())) <= 2
