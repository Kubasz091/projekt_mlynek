from __future__ import annotations

from collections.abc import Sequence

import numpy as np


class HitboxMap(Sequence):
    def __init__(self, height, width):
        self.height = height
        self.width = width
        self.hitbox_array = np.zeros((height, width), dtype=np.uint16)

    def __getitem__(self, item):
        return self.hitbox_array[item]

    def __len__(self):
        return self.hitbox_array.size

    def _sliced_views(self, pos: tuple[int, int], other: HitboxMap | np.ndarray):
        """
        Compute clipped overlap between self.hitbox_array and `other` placed with
        its top-left corner at `pos` (y, x). Returns:
        - a: view into self.hitbox_array for the overlapped region or None if no overlap
        - b: view into `other` for the overlapped region (aligned with `a`) or None
        - bounds: (y0, x0, y1, x1) in self coordinates
        - ibounds: (iy0, ix0, iy1, ix1) in other coordinates
        """
        H, W = self.hitbox_array.shape

        try:
            h, w = other.hitbox_array.shape[:2]  # type: ignore[attr-defined]
        except AttributeError:
            h, w = other.shape[:2]

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

        a = self.hitbox_array[y0:y1, x0:x1]

        try:
            b_full = other.hitbox_array  # type: ignore[attr-defined]
        except AttributeError:
            b_full = other

        b = b_full[iy0:iy1, ix0:ix1]

        return a, b, (y0, x0, y1, x1), (iy0, ix0, iy1, ix1)

    def update_hitbox(self, pos, identifier_hitbox: HitboxMap | np.ndarray):
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

    def clear_hitbox(self, pos, identifier_hitbox: HitboxMap | np.ndarray):
        a, b, _, _ = self._sliced_views(pos, identifier_hitbox)
        if a is None or b is None:
            return
        mask = (b != 0) & (a == b)
        if mask.any():
            a[mask] = 0

    def clear(self):
        self.hitbox_array.fill(0)

    def check_position_id(self, pos):
        return self.hitbox_array[pos]

    def best_overlap_ids(self, pos, other_hitbox: HitboxMap | np.ndarray, ignore_same_ids=True):
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


if __name__ == "__main__":
    hitbox_map = HitboxMap(15, 15)
    print(hitbox_map)

    print()

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
