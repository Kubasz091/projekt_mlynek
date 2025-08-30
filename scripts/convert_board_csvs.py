#!/usr/bin/env python3
"""
Convert legacy CSV board layout files into the new JSON format expected by
data_loaders.objects_reader.load_game_objects.

Output files are written next to the CSVs as graphic_data/board_size_<N>.json.

Schema emitted:
{
  "Field": {
    "dot_<id>": {
      "position": {"y": int, "x": int},
      "texture": {"name": "dot"},
      "connections": {
        "Edge": {
          "class_name": "Edge",
          "connector_data": [
            {"position": {"y": 0, "x": 0}, "obj": null},
            {"position": {"y": 1, "x": 0}, "obj": null},
            {"position": {"y": 0, "x": 1}, "obj": null},
            {"position": {"y": 1, "x": 1}, "obj": null}
          ]
        },
        "Pawn": {
          "class_name": "Pawn",
          "connector_data": [
            {"position": {"y": 0, "x": 0}, "obj": null}
          ]
        }
      }
    },
    ...
  },
  "Edge": {
    "<edge_id>": {
      "position": {"y": int, "x": int},
      "texture": {"name": "horizontal_line" | "vertical_line" | "diagonal_l_r" | "diagonal_r_l"}
    },
    ...
  }
}

Notes:
- We intentionally omit texture "size" to avoid coupling to registry at conversion time.
- Dot connectivity (connected_to) is not embedded here; gameplay can infer paths via edges.
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GD = ROOT / "graphic_data"


@dataclass
class Row:
    element_type: str
    element_id: str
    x: int
    y: int
    connected_to: str
    description: str

    @classmethod
    def from_dict(cls, d: dict[str, str]) -> Row:
        return cls(
            element_type=d["element_type"].strip(),
            element_id=str(d["element_id"]).strip(),
            x=int(d["x_coord"]),
            y=int(d["y_coord"]),
            connected_to=d.get("connected_to", "").strip(),
            description=d.get("description", "").strip(),
        )


def choose_diag_texture(desc: str) -> str:
    d = desc.lower()
    # Prefer vertical direction naming per graphics.json: diagonal_u_d or diagonal_d_u
    if "top" in d:
        return "diagonal_u_d"
    if "bottom" in d:
        return "diagonal_d_u"
    # Fallback heuristics
    if "left_to_right" in d:
        return "diagonal_u_d"  # assume slants downward
    if "right_to_left" in d:
        return "diagonal_u_d"  # same slant, different start
    return "diagonal_u_d"


def convert_csv(path: Path) -> dict:
    # Collect rows
    dot_pos: dict[int, tuple[int, int]] = {}
    dot_conn: dict[int, list[int]] = {}
    horiz: list[tuple[str, int, int]] = []
    vert: list[tuple[str, int, int]] = []
    diag_ud: list[tuple[str, int, int]] = []
    diag_du: list[tuple[str, int, int]] = []

    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        for raw in reader:
            row = Row.from_dict(raw)
            if row.element_type == "dot":
                did = int(row.element_id)
                dot_pos[did] = (row.x, row.y)
                ct = row.connected_to
                dot_conn[did] = [int(x) for x in ct.split(",")] if ct else []
            elif row.element_type == "horizontal_line":
                horiz.append((row.element_id, row.x, row.y))
            elif row.element_type == "vertical_line":
                vert.append((row.element_id, row.x, row.y))
            elif row.element_type == "diagonal_line":
                tex = choose_diag_texture(row.description)
                if tex == "diagonal_u_d":
                    diag_ud.append((row.element_id, row.x, row.y))
                else:
                    diag_du.append((row.element_id, row.x, row.y))

    # Assign numeric Edge IDs in a stable order
    edge_id_map: dict[str, int] = {}
    edges_data: dict[int, dict] = {}
    edge_counter = 1

    def add_edge(src_id: str, x: int, y: int, tex: str):
        nonlocal edge_counter
        eid = edge_counter
        edge_id_map[src_id] = eid
        edges_data[eid] = {
            "id": eid,
            "position": {"y": y, "x": x},
            "texture": {"name": tex},
        }
        edge_counter += 1

    for src, x, y in horiz:
        add_edge(src, x, y, "horizontal_line")
    for src, x, y in vert:
        add_edge(src, x, y, "vertical_line")
    for src, x, y in diag_ud:
        add_edge(src, x, y, "diagonal_u_d")
    for src, x, y in diag_du:
        add_edge(src, x, y, "diagonal_d_u")

    # Build indices for search
    horiz_by_y: dict[int, list[tuple[str, int]]] = {}
    for name, x, y in horiz:
        horiz_by_y.setdefault(y, []).append((name, x))
    for y in horiz_by_y:
        horiz_by_y[y].sort(key=lambda t: t[1])

    vert_by_x: dict[int, list[tuple[str, int]]] = {}
    for name, x, y in vert:
        vert_by_x.setdefault(x, []).append((name, y))
    for x in vert_by_x:
        vert_by_x[x].sort(key=lambda t: t[1])

    diagud_points = [(name, x, y) for name, x, y in diag_ud]
    diagdu_points = [(name, x, y) for name, x, y in diag_du]

    # Pair -> chosen Edge id cache so both dots share the same segment
    pair_edge: dict[frozenset[int], int] = {}

    def choose_horizontal_between(y: int, x1: int, x2: int) -> int | None:
        row = horiz_by_y.get(y + 1, [])  # segments drawn just below
        if not row:
            return None
        lo, hi = sorted((x1, x2))
        # pick the segment whose x is closest to midpoint
        mid = (lo + hi) // 2
        name, _ = min(row, key=lambda t: abs(t[1] - mid))
        return edge_id_map[name]

    def choose_vertical_between(x: int, y1: int, y2: int) -> int | None:
        col = vert_by_x.get(x + 2, [])  # segments drawn just to the right
        if not col:
            return None
        lo, hi = sorted((y1, y2))
        mid = (lo + hi) // 2
        name, _ = min(col, key=lambda t: abs(t[1] - mid))
        return edge_id_map[name]

    def choose_diag_between(x1: int, y1: int, x2: int, y2: int) -> int | None:
        # Pick based on whether the segment goes up->down (u_d) or down->up (d_u)
        points = diagud_points if y2 > y1 else diagdu_points
        if not points:
            return None
        midx, midy = (x1 + x2) // 2, (y1 + y2) // 2
        name, _, _ = min(points, key=lambda t: abs(t[1] - midx) + abs(t[2] - midy))
        return edge_id_map[name]

    # Build Field objects with ids and connections
    fields_data: dict[int, dict] = {}
    for did, (x, y) in dot_pos.items():
        connectors = [
            {"position": {"y": 0, "x": 0}, "obj": None},  # up-left
            {"position": {"y": 1, "x": 0}, "obj": None},  # down-left
            {"position": {"y": 0, "x": 1}, "obj": None},  # up-right
            {"position": {"y": 1, "x": 1}, "obj": None},  # down-right
        ]

        def set_slot(slot: tuple[int, int], eid: int | None, _connectors=connectors):
            if eid is None:
                return
            idx_map = {(0, 0): 0, (1, 0): 1, (0, 1): 2, (1, 1): 3}
            _connectors[idx_map[slot]]["obj"] = {"id": eid, "class_name": "Edge"}

        for nb in dot_conn.get(did, []):
            pair = frozenset((did, nb))
            if pair in pair_edge:
                eid = pair_edge[pair]
                nx, ny = dot_pos[nb]
            else:
                nx, ny = dot_pos[nb]
                if ny == y:
                    eid = choose_horizontal_between(y, x, nx)
                elif nx == x:
                    eid = choose_vertical_between(x, y, ny)
                else:
                    eid = choose_diag_between(x, y, nx, ny)
                if eid is not None:
                    pair_edge[pair] = eid

            # decide slot by relative quadrant and placement
            dx = (1 if nx > x else -1) if nx != x else 0
            dy = (1 if ny > y else -1) if ny != y else 0
            if dy == 0 and dx != 0:
                # horizontal: segments are below (y+1). pick down-<side>
                set_slot((1, 1) if dx == 1 else (1, 0), eid)
            elif dx == 0 and dy != 0:
                # vertical: segments are to the right (x+2). pick <up/down>-right
                set_slot((1, 1) if dy == 1 else (0, 1), eid)
            else:
                # diagonal by quadrant
                if dx == 1 and dy == 1:
                    set_slot((1, 1), eid)
                elif dx == 1 and dy == -1:
                    set_slot((0, 1), eid)
                elif dx == -1 and dy == 1:
                    set_slot((1, 0), eid)
                elif dx == -1 and dy == -1:
                    set_slot((0, 0), eid)

        fields_data[did] = {
            "id": did,
            "position": {"y": y, "x": x},
            "texture": {"name": "dot"},
            "connections": {
                "Edge": {"class_name": "Edge", "connector_data": connectors},
                "Pawn": {
                    "class_name": "Pawn",
                    "connector_data": [{"position": {"y": 0, "x": 0}, "obj": None}],
                },
            },
        }

    # Emit Edge first so loader registers edges before fields with connectors
    return {"Edge": edges_data, "Field": fields_data}


def write_json(data: dict, out_path: Path) -> None:
    out_path.write_text(json.dumps(data, indent=4, ensure_ascii=False))


def main() -> None:
    sizes = [3, 6, 9, 12]
    for size in sizes:
        csv_path = GD / f"board_size_{size}.csv"
        if not csv_path.exists():
            print(f"[skip] missing {csv_path}")
            continue
        data = convert_csv(csv_path)
        out_path = GD / f"board_size_{size}.json"
        write_json(data, out_path)
    total = sum(len(d) for d in data.values())
    rel = out_path.relative_to(ROOT)
    print(f"[ok] wrote {rel} ({total} objects)")


if __name__ == "__main__":
    main()
