import csv
import json
import os


class GraphicData:
    def __init__(self, size: int):
        self._graphics_data = self._load_graphics_from_json()
        self._size = size
        self._board_data = self._load_board_data_from_csv(size)

    def _load_graphics_from_json(self) -> dict:
        """Load graphics data from JSON file."""
        json_path = "/home/jszubzda/projekt_mlynek/graphic_data/graphics.json"

        if not os.path.exists(json_path):
            raise FileNotFoundError(f"Graphics JSON file not found: {json_path}")

        with open(json_path, encoding="utf-8") as jsonfile:
            return json.load(jsonfile)

    def _load_board_data_from_csv(self, size: int) -> dict:
        """Load board data from CSV file based on board size."""
        csv_path = f"/home/jszubzda/projekt_mlynek/graphic_data/board_size_{size}.csv"

        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"Board data CSV file not found: {csv_path}")

        board_data = {
            "dot": [],
            "connected_dots": {},
            "horizontal_line": [],
            "vertical_line": [],
            "diagonal_l_r": [],
            "diagonal_r_l": [],
        }

        with open(csv_path, newline="") as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                element_type = row["element_type"]
                x_coord = int(row["x_coord"])
                y_coord = int(row["y_coord"])

                if element_type == "dot":
                    board_data["dot"].append((x_coord, y_coord))

                    # Handle connected dots
                    element_id = int(row["element_id"])
                    connected_to = row["connected_to"].strip()
                    if connected_to:
                        connections = tuple(int(x) for x in connected_to.split(","))
                        board_data["connected_dots"][element_id] = connections

                elif element_type == "horizontal_line":
                    board_data["horizontal_line"].append((x_coord, y_coord))

                elif element_type == "vertical_line":
                    board_data["vertical_line"].append((x_coord, y_coord))

                elif element_type == "diagonal_line":
                    description = row["description"]
                    if "left_to_right" in description:
                        board_data["diagonal_l_r"].append((x_coord, y_coord))
                    elif "right_to_left" in description:
                        board_data["diagonal_r_l"].append((x_coord, y_coord))

        return board_data

    @property
    def board_data(self):
        return self._board_data

    @property
    def graphics_data(self):
        return self._graphics_data

    @property
    def size(self):
        return self._size
