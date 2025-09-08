from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import numpy as np


class _BaseGrid(Sequence):
    """Internal base for 2D id grids with shared slicing helpers."""

    def __init__(self, height: int, width: int):
        self.height = height
        self.width = width

    # Subclasses must provide the underlying numpy array
    def _get_array(self) -> np.ndarray:  # pragma: no cover - abstract-like
        raise NotImplementedError

    def __getitem__(self, item):
        return self._get_array()[item]

    def __len__(self):
        return self._get_array().size

    def _sliced_views(self, pos: tuple[int, int], other: Any):
        """
        Compute clipped overlap between self array and `other` placed with its top-left
        corner at `pos` (y, x). Returns views (a, b, bounds, ibounds).
        Looks for a numpy array on `other` under the attribute name "hitbox_array";
        if none found, assumes `other` itself is a numpy array.
        """
        self_arr = self._get_array()
        H, W = self_arr.shape

        # Dimensions of other
        b_full = getattr(other, "hitbox_array", other)
        h, w = b_full.shape[:2]

        y0 = max(0, pos[0])
        x0 = max(0, pos[1])
        y1 = min(H, pos[0] + h)
        x1 = min(W, pos[1] + w)

        if y0 >= y1 or x0 >= x1:
            return None, None, (y0, x0, y1, x1), (0, 0, 0, 0)

        iy0 = y0 - pos[0]
        ix0 = x0 - pos[1]
        iy1 = iy0 + (y1 - y0)
        ix1 = ix0 + (x1 - x0)

        a = self_arr[y0:y1, x0:x1]
        b = b_full[iy0:iy1, ix0:ix1]
        return a, b, (y0, x0, y1, x1), (iy0, ix0, iy1, ix1)

    def clear(self):
        self._get_array().fill(0)


class CoOccurrenceMap(_BaseGrid):
    def __init__(self, height, width):
        super().__init__(height, width)
        self.hitbox_array = np.zeros((height, width), dtype=np.uint16)

    def _get_array(self) -> np.ndarray:
        return self.hitbox_array

    # Inherit _sliced_views from base (tries common attribute names by default)

    def update_hitbox(self, pos, identifier_hitbox: Any):
        """
        Place identifier_hitbox at top-left pos.
        Heuristic on overlap:
        - Always place our center (if inside and non-zero).
        - Keep all non-overlapping cells.
        - Overwrite up to half of overlapped cells, picked from the center toward
          the opposite direction of the overlap, preferring cells closest to the center.
        """
        a, b, (y0, x0, y1, x1), (iy0, ix0, _, _) = self._sliced_views(pos, identifier_hitbox)
        if a is None or b is None:
            return

        try:
            h, w = identifier_hitbox.hitbox_array.shape[:2]  # type: ignore[attr-defined]
        except AttributeError:
            h, w = identifier_hitbox.shape[:2]

        id_mask = b != 0
        if not id_mask.any():
            return

        occupied = a != 0
        overlap = occupied & id_mask
        free = (~occupied) & id_mask

        # Center handling
        cy_full, cx_full = h // 2, w // 2
        cy = cy_full - iy0
        cx = cx_full - ix0
        center_inside = (0 <= cy < (y1 - y0)) and (0 <= cx < (x1 - x0))
        center_local = (int(cy), int(cx)) if center_inside else None

        # Fast path: no overlap
        if not overlap.any():
            a[id_mask] = b[id_mask]
            return

        # Overlap direction: centroid of overlapped cells relative to our center
        if center_inside:
            yy, xx = np.nonzero(overlap)
            oy = yy.mean() - cy
            ox = xx.mean() - cx
            v = np.array([oy, ox], dtype=float)
            nv = float(np.hypot(v[0], v[1]))
            v = v / nv if nv > 1e-12 else np.array([0.0, 0.0], dtype=float)
        else:
            v = np.array([0.0, 0.0], dtype=float)

        # Opposite half-plane mask
        Y, X = np.indices(a.shape)
        if center_inside:
            relY = Y - cy
            relX = X - cx
            dot = relY * v[0] + relX * v[1]
            opposite_half = dot <= 0.0
        else:
            relY = Y - (Y.shape[0] // 2)
            relX = X - (X.shape[1] // 2)
            opposite_half = np.ones_like(a, dtype=bool)

        # Budget: up to half of overlapped cells
        overlap_count = int(overlap.sum())
        budget = (overlap_count + 1) // 2  # ceil(O/2)

        # Choose candidates on opposite side, closest to center first
        dist2 = relY * relY + relX * relX
        cand = overlap & opposite_half
        yy_c, xx_c = np.nonzero(cand)
        if len(yy_c) == 0:
            yy_c, xx_c = np.nonzero(overlap)
        d2_c = dist2[yy_c, xx_c]
        order = np.argsort(d2_c, kind="stable")
        yy_sel = yy_c[order][:budget]
        xx_sel = xx_c[order][:budget]

        # Final mask: center, all free cells, and selected overlapped cells
        final_mask = np.zeros_like(a, dtype=bool)
        if center_inside and b[center_local] != 0:
            final_mask[center_local] = True
        final_mask |= free
        if len(yy_sel) > 0:
            final_mask[yy_sel, xx_sel] = True

        write_mask = final_mask & id_mask
        a[write_mask] = b[write_mask]

    def clear_hitbox(self, pos, identifier_hitbox: Any):
        a, b, _, _ = self._sliced_views(pos, identifier_hitbox)
        if a is None or b is None:
            return
        mask = (b != 0) & (a == b)
        if mask.any():
            a[mask] = 0

    def check_position_id(self, pos):
        return self.hitbox_array[pos]

    def best_overlap_ids(self, pos, other_hitbox: Any, ignore_same_ids=False):
        a, b, _, _ = self._sliced_views(pos, other_hitbox)
        if a is None or b is None:
            return (0, 0, 0)

        mask = (a != 0) & (b != 0)
        if not mask.any():
            return (0, 0, 0)

        Avals = a[mask].astype(np.int64, copy=False)
        Bvals = b[mask].astype(np.int64, copy=False)

        Au, Ai = np.unique(Avals, return_inverse=True)
        Bu, Bi = np.unique(Bvals, return_inverse=True)

        combined = Ai * len(Bu) + Bi
        counts = np.bincount(combined)

        if ignore_same_ids and counts.size > 0:
            # Zero out counts where the pair corresponds to the same id on both sides
            nB = len(Bu)
            idx = np.arange(counts.size, dtype=np.int64)
            iA_idx = (idx // nB).tolist()
            iB_idx = (idx % nB).tolist()
            same_pair_mask = np.array([int(Au[ia]) == int(Bu[ib]) for ia, ib in zip(iA_idx, iB_idx)], dtype=bool)
            if same_pair_mask.any():
                counts[same_pair_mask] = 0
            if counts.sum() == 0:
                return (0, 0, 0)
        k = int(counts.argmax())
        count = int(counts[k])

        iA, iB = divmod(k, len(Bu))
        idA = int(Au[iA])
        idB = int(Bu[iB])
        return (idA, idB, count)

    def to_dict(self):
        return {
            "width": self.width,
            "height": self.height,
            "hitbox_array": self.hitbox_array.tolist(),
        }

    @classmethod
    def from_dict(cls, dict):
        width = dict.get("width", 0)
        height = dict.get("height", 0)
        hitbox_array = dict.get("hitbox_array", None)

        instance = cls(width, height)

        if hitbox_array is not None:
            instance.hitbox_array = np.array(hitbox_array, dtype=np.uint16)

        return instance

    def __str__(self):
        lines = []
        for row in self.hitbox_array:
            line = " ".join(("  " if int(val) == 0 else f"{int(val):2}") for val in row)
            lines.append(line)
        return "\n".join(lines)


class FullCoverageMap(_BaseGrid):
    """
    Track template ids and detect those fully covered by an input array.
    Also supports simple, performance-focused updates with id preservation and balancing.
    """

    def __init__(self, height: int, width: int):
        super().__init__(height, width)
        self.hitbox_array = np.zeros((height, width), dtype=np.uint16)

    def _get_array(self) -> np.ndarray:
        return self.hitbox_array

    def overlay_ids(self, pos: tuple[int, int], id_array: Any):
        """
        Overlay id_array (non-zero cells are required positions for a given id)
        at top-left pos. Preserve at least one cell of every previously present id
        in the overlapped area and keep counts among ids roughly balanced.
        """
        a, b, _, _ = self._sliced_views(pos, id_array)
        if a is None or b is None:
            return

        id_mask = b != 0
        if not id_mask.any():
            return

        # Overlap region: only cells where existing ids meet the incoming ids
        overlap = (a != 0) & id_mask

        # Start from direct overlay everywhere b is non-zero
        new = a.copy()
        new[id_mask] = b[id_mask]

        # If there's no overlap, we are done
        if not overlap.any():
            a[id_mask] = b[id_mask]
            return

        # Ensure previously present ids in the overlap keep at least one cell inside the overlap
        prev_ids = np.unique(a[overlap])
        prev_ids = prev_ids[prev_ids != 0]
        for pid in prev_ids:
            if not np.any(new[overlap] == pid):
                yy, xx = np.nonzero((a == pid) & overlap)
                if len(yy) > 0:
                    new[(yy[0], xx[0])] = pid
                else:
                    # fallback: donate from current majority within the overlap
                    ids_all, counts_all = np.unique(new[overlap], return_counts=True)
                    mask_nz = ids_all != 0
                    ids_nz = ids_all[mask_nz]
                    counts_nz = counts_all[mask_nz]
                    if len(ids_nz) > 0:
                        donor = int(ids_nz[np.argmax(counts_nz)])
                        yy2, xx2 = np.nonzero((new == donor) & overlap)
                        if len(yy2) > 0:
                            new[(yy2[0], xx2[0])] = pid

        def balance_ids(new_slice: np.ndarray, pref: np.ndarray, region_mask: np.ndarray):
            ids_now, counts_now = np.unique(new_slice[region_mask], return_counts=True)
            mask_nz = ids_now != 0
            ids_now = ids_now[mask_nz]
            counts_now = counts_now[mask_nz]
            if len(ids_now) <= 1:
                return new_slice

            def pick_donor_cell(donor_id: int, recipient_id: int):
                m_donor = (new_slice == donor_id) & region_mask
                if not m_donor.any():
                    return None
                yy, xx = np.nonzero(m_donor & (pref == recipient_id))
                if len(yy) > 0:
                    return int(yy[0]), int(xx[0])
                yy, xx = np.nonzero(m_donor & (pref != donor_id))
                if len(yy) > 0:
                    return int(yy[0]), int(xx[0])
                yy, xx = np.nonzero(m_donor)
                if len(yy) > 0:
                    return int(yy[0]), int(xx[0])
                return None

            guard = 0
            while guard < 1024:
                guard += 1
                ids_now, counts_now = np.unique(new_slice[region_mask], return_counts=True)
                mask_nz = ids_now != 0
                ids_now = ids_now[mask_nz]
                counts_now = counts_now[mask_nz]
                if len(ids_now) <= 1:
                    break
                id_list = [int(i) for i in ids_now]
                count_map = {int(i): int(c) for i, c in zip(id_list, counts_now)}
                donor_id = max(id_list, key=lambda k: count_map[k])
                recipient_id = min(id_list, key=lambda k: count_map[k])
                if count_map[donor_id] - count_map[recipient_id] <= 1:
                    break
                cell = pick_donor_cell(donor_id, recipient_id)
                if cell is None:
                    break
                new_slice[cell[0], cell[1]] = recipient_id
            return new_slice

        pref = np.where(b != 0, b.astype(np.uint16, copy=False), a.astype(np.uint16, copy=False))
        new = balance_ids(new, pref, overlap)
        a[:, :] = new

    def clear_ids(self, pos: tuple[int, int], id_array: Any):
        a, b, _, _ = self._sliced_views(pos, id_array)
        if a is None or b is None:
            return
        mask = (b != 0) & (a == b)
        if mask.any():
            a[mask] = 0

    def mark_points(self, points: list[tuple[int, int]], id_value: int):
        """Mark non-contiguous positions directly by coordinates for a given id_value."""
        if not points:
            return
        ys = np.fromiter((p[0] for p in points), dtype=np.int64)
        xs = np.fromiter((p[1] for p in points), dtype=np.int64)
        in_bounds = (ys >= 0) & (ys < self.height) & (xs >= 0) & (xs < self.width)
        if not np.any(in_bounds):
            return
        ys = ys[in_bounds]
        xs = xs[in_bounds]
        self.hitbox_array[ys, xs] = np.uint16(id_value)

    def to_dict(self):
        return {
            "width": self.width,
            "height": self.height,
            "hitbox_array": self.hitbox_array.tolist(),
        }

    @classmethod
    def from_dict(cls, dict):
        width = dict.get("width", 0)
        height = dict.get("height", 0)
        arr = dict.get("hitbox_array", None)

        instance = cls(height, width)

        if arr is not None:
            instance.hitbox_array = np.array(arr, dtype=np.uint16)

        return instance

    def fully_covered_ids(self, cover_map: Any) -> tuple[list[int], int]:
        """
        Given a coverage/occupancy map (non-zero means "covered"), return the list
        of ids that are fully covered and the total count.
        """
        try:
            pawns = cover_map.hitbox_array  # type: ignore[attr-defined]
        except AttributeError:
            pawns = cover_map

        completed: list[int] = []
        ids = np.unique(self.hitbox_array)
        ids = ids[ids != 0]
        for mid in ids.astype(int):
            mask = self.hitbox_array == mid
            if mask.any():
                # Vectorized check: all required cells covered by any pawn
                if np.all(pawns[mask] != 0):
                    completed.append(mid)
        return completed, len(completed)

    def __str__(self):
        lines = []
        for row in self.hitbox_array:
            line = " ".join(("  " if int(val) == 0 else f"{int(val):2}") for val in row)
            lines.append(line)
        return "\n".join(lines)


if __name__ == "__main__":
    # Basic CoOccurrenceMap test
    print("-- CoOccurrenceMap basic test --")
    hitbox_map = CoOccurrenceMap(15, 15)
    print(hitbox_map)

    field_identifier_hitbox = np.full((3, 3), 1, dtype=np.uint16)
    curr_pos_field = (5, 5)
    hitbox_map.update_hitbox(curr_pos_field, field_identifier_hitbox)
    print(hitbox_map)

    print(hitbox_map.check_position_id((6, 5)))
    print(hitbox_map.check_position_id((7, 7)))
    print(hitbox_map.check_position_id((8, 5)))

    # moving the hitbox
    hitbox_map.clear_hitbox(curr_pos_field, field_identifier_hitbox)
    curr_pos_field = (10, 10)
    hitbox_map.update_hitbox(curr_pos_field, field_identifier_hitbox)
    print(hitbox_map)

    pawn_curr_pos = (13, 9)
    pawn_identifier_hitbox = np.full((3, 3), 2, dtype=np.uint16)

    hitbox_map.update_hitbox(pawn_curr_pos, pawn_identifier_hitbox)
    print(hitbox_map)

    hitbox_map.clear_hitbox(curr_pos_field, field_identifier_hitbox)
    print(hitbox_map)

    # FullCoverageMap tests
    print("\n-- FullCoverageMap tests --")
    mh = FullCoverageMap(12, 12)

    # 1) Non-contiguous mill positions (three separate squares)
    mill_id = 9
    pts = [(2, 2), (2, 6), (2, 10)]
    mh.mark_points(pts, mill_id)

    print(mh)

    # Occupy with pawns at the required points
    pawns = np.zeros_like(mh.hitbox_array, dtype=np.uint16)

    pts2 = [(2, 2), (2, 6), (2, 10)]
    for y, x in pts2:
        pawns[y, x] = 1

    completed, cnt = mh.fully_covered_ids(pawns)

    print("completed includes 9:", (mill_id in completed), "count:", cnt)

    # 2) Overlapping mills with balancing/preservation
    arrA = np.zeros((2, 4), dtype=np.uint16)
    arrA[:] = 101
    arrB = np.zeros((2, 4), dtype=np.uint16)
    arrB[:] = 202
    mh.overlay_ids((5, 5), arrA)

    print(mh)
    mh.overlay_ids((5, 6), arrB)  # overlaps with A

    print(mh)
    # Check balance only within the true overlap between arrA and arrB
    overlap_region = (slice(5, 7), slice(6, 9))
    sub = mh.hitbox_array[overlap_region]
    unique, counts = np.unique(sub[sub != 0], return_counts=True)
    if unique.size > 0:
        spread_ok = bool((np.max(counts) - np.min(counts)) <= 1)
    else:
        spread_ok = True
    print("balance within +/-1:", spread_ok)
