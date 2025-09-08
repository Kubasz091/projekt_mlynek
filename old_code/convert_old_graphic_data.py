if __name__ == "__main__":
    import sys
    from os.path import abspath, dirname

    sys.path.append(dirname(dirname(abspath(__file__))))

import json
import os
from typing import cast

import numpy as np

from data_loaders.game_object_registry import (
    _GAME_OBJECT_REGISTRY,
    change_board_size,
    game_object_registry_ids_dict,
    game_objects_to_dict,
    reasing_put_away_objs_ids,
    register_game_object,
    reload_hitboxes,
)
from data_loaders.texture_registry import _TERMINAL_GRAPHICS_PATH, load_textures
from game_objects.board import Board
from game_objects.edge import Edge
from game_objects.field import Field
from game_objects.hitboxes import FullCoverageMap
from game_objects.pawn import PawnP1, PawnP2
from old_code.graphic_data import GraphicData
from utils.connection_list import Connector, ConnectorList

for size in range(3, 15, 3):
    graphic_data = GraphicData(size)

    board_data = graphic_data.board_data

    dot_positions = board_data["dot"]

    connection_data = board_data["connected_dots"]

    horizontal_line_pos = board_data["horizontal_line"]

    vertical_line_pos = board_data["vertical_line"]

    diagonal_u_d_pos = board_data.get("diagonal_u_d", None)

    diagonal_d_u_pos = board_data.get("diagonal_d_u", None)

    x_adjustment = 10

    if size == 12:
        x_adjustment = 18

    tmp = []
    for pos in dot_positions:
        tmp.append((pos[1], pos[0] + x_adjustment))
    dot_positions = tmp

    tmp = []
    for pos in horizontal_line_pos:
        tmp.append((pos[1], pos[0] + x_adjustment))
    horizontal_line_pos = tmp

    tmp = []
    for pos in vertical_line_pos:
        tmp.append((pos[1], pos[0] + x_adjustment))
    vertical_line_pos = tmp

    if diagonal_u_d_pos is not None:
        tmp = []
        for pos in diagonal_u_d_pos:
            tmp.append((pos[1] + 1, pos[0] + 1 + x_adjustment))
        diagonal_u_d_pos = tmp

    if diagonal_d_u_pos is not None:
        tmp = []
        for pos in diagonal_d_u_pos:
            tmp.append((pos[1] + 1, pos[0] + 1 + x_adjustment))
        diagonal_d_u_pos = tmp

    print("Dot Positions:", dot_positions)
    print("Connection Data:", connection_data)
    print("Horizontal Line Positions:", horizontal_line_pos)
    print("Vertical Line Positions:", vertical_line_pos)
    print("Diagonal Up-Down Positions:", diagonal_u_d_pos)
    print("Diagonal Down-Up Positions:", diagonal_d_u_pos)

    load_textures()

    max_x = 0
    max_y = 0
    for pos in dot_positions:
        if pos[1] + 5 > max_x:
            max_x = pos[1] + 5
        if pos[0] + 2 > max_y:
            max_y = pos[0] + 2
        obj = Field(position={"y": pos[0], "x": pos[1]}, texture={"name": "dot"}, allign_offset=1)
        register_game_object(obj)

    change_board_size((max_y + 1, max_x + 1 + x_adjustment))

    connection_dict = {
        "Field": {
            "class_name": "Edge",
            "connector_data": {
                1: {"id": 1, "position": {"y": 0, "x": 0}, "allign_offset": 1, "obj": None},
                2: {"id": 2, "position": {"y": 0, "x": 5}, "allign_offset": 1, "obj": None},
            },
        }
    }
    for pos in horizontal_line_pos:
        obj = Edge(
            position={"y": pos[0], "x": pos[1]},
            texture={"name": "horizontal_line"},
            allign_offset=1,
            connections=connection_dict,
        )
        register_game_object(obj)

    connection_dict = {
        "Field": {
            "class_name": "Edge",
            "connector_data": {
                1: {"id": 1, "position": {"y": 0, "x": 0}, "allign_offset": 1, "obj": None},
                2: {"id": 2, "position": {"y": 2, "x": 0}, "allign_offset": 1, "obj": None},
            },
        }
    }

    for pos in vertical_line_pos:
        obj = Edge(
            position={"y": pos[0], "x": pos[1]},
            texture={"name": "vertical_line"},
            allign_offset=1,
            connections=connection_dict,
        )
        register_game_object(obj)

    if diagonal_u_d_pos is not None:
        connection_dict = {
            "Field": {
                "class_name": "Edge",
                "connector_data": {
                    1: {"id": 1, "position": {"y": 0, "x": 0}, "allign_offset": 1, "obj": None},
                    2: {"id": 2, "position": {"y": 2, "x": 5}, "allign_offset": 1, "obj": None},
                },
            }
        }

        for pos in diagonal_u_d_pos:
            obj = Edge(
                position={"y": pos[0], "x": pos[1]},
                texture={"name": "diagonal_u_d"},
                allign_offset=1,
                connections=connection_dict,
            )
            register_game_object(obj)

    if diagonal_d_u_pos is not None:
        connection_dict = {
            "Field": {
                "class_name": "Edge",
                "connector_data": {
                    1: {"id": 1, "position": {"y": 2, "x": 0}, "allign_offset": 1, "obj": None},
                    2: {"id": 2, "position": {"y": 0, "x": 5}, "allign_offset": 1, "obj": None},
                },
            }
        }

        for pos in diagonal_d_u_pos:
            obj = Edge(
                position={"y": pos[0], "x": pos[1]},
                texture={"name": "diagonal_d_u"},
                allign_offset=1,
                connections=connection_dict,
            )
            register_game_object(obj)

    reasing_put_away_objs_ids()
    reload_hitboxes()

    print(game_object_registry_ids_dict())

    sucessfull_connects = 0

    # add connectors to the fields based on the proximity of connectors of edges
    for edge_obj in _GAME_OBJECT_REGISTRY["Edge"].values():
        edge = cast(Edge, edge_obj)
        for _class_name, connection_list in edge.connections.items():
            for connector in connection_list._dict.values():
                _point_up = False
                _point_down = False
                _point_left = False
                _point_right = False

                if edge.texture.size[0] > 1:
                    if connector.pos[0] < 1:
                        _point_up = True
                    elif connector.pos[0] > 1:
                        _point_down = True

                if edge.texture.size[1] > 2:
                    if connector.pos[1] < 2:
                        _point_left = True
                    elif connector.pos[1] > 2:
                        _point_right = True

                if (_point_up and _point_down) or (_point_left and _point_right):
                    raise ValueError

                edge_pos = edge.position
                absolute_conn_pos = (edge_pos.y + connector.pos[0], edge_pos.x + connector.pos[1])

                if _point_up and not _point_left and not _point_right:  # look for a field above
                    look_pos = (absolute_conn_pos[0] - 1, absolute_conn_pos[1])
                elif _point_down and not _point_left and not _point_right:  # look for a field below
                    look_pos = (absolute_conn_pos[0] + 1, absolute_conn_pos[1])
                elif _point_left and not _point_up and not _point_down:  # look for a field to the left
                    look_pos = (absolute_conn_pos[0], absolute_conn_pos[1] - 1)
                elif _point_right and not _point_up and not _point_down:  # look for a field to the right
                    look_pos = (absolute_conn_pos[0], absolute_conn_pos[1] + 1)
                elif _point_up and _point_left:  # look for a field to the top-left
                    look_pos = (absolute_conn_pos[0] - 1, absolute_conn_pos[1] - 1)
                elif _point_up and _point_right:  # look for a field to the top-right
                    look_pos = (absolute_conn_pos[0] - 1, absolute_conn_pos[1] + 1)
                elif _point_down and _point_left:  # look for a field to the bottom-left
                    look_pos = (absolute_conn_pos[0] + 1, absolute_conn_pos[1] - 1)
                elif _point_down and _point_right:  # look for a field to the bottom-right
                    look_pos = (absolute_conn_pos[0] + 1, absolute_conn_pos[1] + 1)
                else:
                    raise ValueError(f"Invalid connector position: {connector.pos} for edge at {edge.position}")

                for field_obj in _GAME_OBJECT_REGISTRY["Field"].values():
                    field = cast(Field, field_obj)
                    field_pos = field.position
                    possible_field_connector_positions = [
                        (field_pos.y, field_pos.x + 2),  # up
                        (field_pos.y + 2, field_pos.x + 2),  # down-
                        (field_pos.y + 1, field_pos.x),  # left
                        (field_pos.y + 1, field_pos.x + 5),  # right
                        (field_pos.y, field_pos.x),  # up-left
                        (field_pos.y, field_pos.x + 5),  # up-right
                        (field_pos.y + 2, field_pos.x),  # down-left
                        (field_pos.y + 2, field_pos.x + 5),  # down-right
                    ]
                    for possible_connector_pos in possible_field_connector_positions:
                        if look_pos == possible_connector_pos:
                            print(
                                "Connecting edge at",
                                edge.position,
                                "to field at",
                                field.position,
                                "via connector at",
                                connector.pos,
                                "(absolute pos:",
                                absolute_conn_pos,
                                ")",
                            )
                            rel_pos = (
                                look_pos[0] - field_pos.y,
                                look_pos[1] - field_pos.x,
                            )

                            # Ensure ConnectorList exists on Field
                            if "Edge" not in field.connections:
                                field.connections["Edge"] = ConnectorList(Field.__name__)

                            # Append a new connector to Field and get its id

                            field_conn_id = field.connections["Edge"].append(pos=rel_pos, allign_offset=1)
                            field_connector = field.connections["Edge"]._dict[field_conn_id]

                            # Bi-directional connect between Edge and Field
                            edge.connections["Field"].connect(field, field_connector, my_connector_id=connector.id)
                            field.connections["Edge"].connect(edge, connector, my_connector_id=field_conn_id)

                            # Optionally update connector hitbox maps
                            if hasattr(edge, "update_hitbox_map"):
                                edge.update_hitbox_map("Field")
                            if hasattr(field, "update_hitbox_map"):
                                field.update_hitbox_map("Edge")

                            sucessfull_connects += 1
                            break

    # change unused edge connectors from field connectors to edge connectors
    changed_connectors = 0
    for edge_obj in _GAME_OBJECT_REGISTRY["Edge"].values():
        edge = cast(Edge, edge_obj)
        connectors_to_reasign = []
        connectors_to_delete = []
        for cid, connector in list(edge.connections["Field"]._dict.items()):
            if connector.obj is None:
                connectors_to_reasign.append(connector.to_dict())
                connectors_to_delete.append(cid)

        for cid in connectors_to_delete:
            del edge.connections["Field"]._dict[cid]

        if connectors_to_reasign:
            if "Edge" not in edge.connections:
                edge.connections["Edge"] = ConnectorList("Edge")

            for conn_data in connectors_to_reasign:
                conn_obj = Connector.from_dict(conn_data)
                # Preserve id if free, else auto-assign via append
                cid = conn_obj.id if hasattr(conn_obj, "id") else None
                if cid and cid not in edge.connections["Edge"]._dict:
                    edge.connections["Edge"]._dict[cid] = conn_obj
                else:
                    edge.connections["Edge"].append(
                        pos=(conn_obj.pos[0], conn_obj.pos[1]),
                        allign_offset=conn_obj.allign_offset,
                    )
                changed_connectors += 1
            edge.update_hitbox_map("Edge")

    edge_connections = 0

    # connect edges that are a part of a long edge
    for edge in _GAME_OBJECT_REGISTRY["Edge"].values():
        try:
            edge.try_connect("Edge")
            edge_connections += 1
        except ValueError:
            pass

    print(f"Changed {changed_connectors} edge connectors from field connectors to edge connectors.")
    print(f"Sucessfully connected {sucessfull_connects} fields and {edge_connections} edges. In the board of size {size}.")

    if size == 12:
        board_data = {
            "id": 1,
            "connections": {
                "PawnP1": {
                    "class_name": "PawnP1",
                    "connector_data": {
                        i + 1: {
                            "id": i + 1,
                            "position": {"y": 1 + (4 * (i % 6)), "x": 2 + (8 * (i // 6))},
                            "allign_offset": 0,
                            "obj": None,
                        }
                        for i in range(size)
                    },
                },
                "PawnP2": {
                    "class_name": "PawnP2",
                    "connector_data": {
                        i + 1: {
                            "id": i + 1,
                            "position": {"y": 1 + (4 * (i % 6)), "x": max_x + 7 + (8 * (i // 6))},
                            "allign_offset": 0,
                            "obj": None,
                        }
                        for i in range(size)
                    },
                },
            },
        }
    else:
        board_data = {
            "id": 1,
            "connections": {
                "PawnP1": {
                    "class_name": "PawnP1",
                    "connector_data": {
                        i + 1: {
                            "id": i + 1,
                            "position": {"y": 1 + (4 * i), "x": 2},
                            "allign_offset": 0,
                            "obj": None,
                        }
                        for i in range(size)
                    },
                },
                "PawnP2": {
                    "class_name": "PawnP2",
                    "connector_data": {
                        i + 1: {
                            "id": i + 1,
                            "position": {"y": 1 + (4 * i), "x": max_x + 7},
                            "allign_offset": 0,
                            "obj": None,
                        }
                        for i in range(size)
                    },
                },
            },
        }

    # Board now requires size argument
    board = Board(**board_data)  # (max_y, max_x + 10)
    register_game_object(board)

    # pawn_connection_data = {
    #     "Board": {
    #         "class_name": "Board",
    #         "connector_data": [
    #             {"position": {"y": 1, "x": 2}, "obj": {"id": 1, "class_name": "Board"}},
    #         ],
    #     }
    # }

    for class_name, connection_list in board.connections.items():
        for connector_id, connector in connection_list._dict.items():
            if class_name == "PawnP1":
                obj = PawnP1(
                    position={"y": connector.pos.y - 1, "x": connector.pos.x - 2},
                    texture={"name": "pawn_player1"},
                )
            elif class_name == "PawnP2":
                obj = PawnP2(
                    position={"y": connector.pos.y - 1, "x": connector.pos.x - 2},
                    texture={"name": "pawn_player2"},
                )
            else:
                raise ValueError(f"Unknown class name in board connections: {class_name}")
            register_game_object(obj)
            # Explicitly connect board<->pawn using their connectors
            # Ensure pawn has 'Board' ConnectorList
            if "Board" not in obj.connections:
                obj.connections["Board"] = ConnectorList(obj.__class__.__name__)
                obj.connections["Board"].append(pos=(1, 2), allign_offset=0)
            # my_connector_id for pawn is 1 (only one connector)
            pawn_connector = obj.connections["Board"]._dict[1]
            board.connections[class_name].connect(obj, pawn_connector, my_connector_id=connector_id)
            board.update_hitbox_map()

            obj.connections["Board"].connect(board, connector, my_connector_id=1)
            obj.update_hitbox_map()

    reasing_put_away_objs_ids()

    fc_map = FullCoverageMap(max_y + 1, max_x + 1 + x_adjustment)

    curr_mill_id = 1

    # y, x
    direction_map = {
        (1, 5): "right",
        (1, 0): "left",
        (0, 2): "up",
        (2, 2): "down",
        (2, 5): "down-right",
        (0, 5): "up-right",
        (2, 0): "down-left",
        (0, 0): "up-left",
    }

    def find_next_field_in_direction(start_field, direction, direction_map):
        for connector in start_field.connections["Edge"]._dict.values():
            if connector.obj is not None:
                # direction check
                connector_direction = direction_map.get((connector.pos.y, connector.pos.x), None)
                if connector_direction == direction:
                    # find the field on the other side of the edge
                    next_field = None
                    current_edge = connector.obj
                    last_connector = connector.connector

                    while next_field is None:
                        if len(current_edge.connections["Field"]) > 0:
                            for field_obj_connector in current_edge.connections["Field"]._dict.values():
                                field = field_obj_connector.obj
                                if field.id != start_field.id:
                                    next_field = field
                                    return next_field, connector, field_obj_connector.connector

                        for edge_connector in current_edge.connections["Edge"]._dict.values():
                            if edge_connector.id != last_connector.id and edge_connector.obj is not None:
                                last_connector = edge_connector.connector
                                current_edge = edge_connector.obj
                                break
        return None, None, None

    help_dict = {}
    # create mills
    for field_obj in _GAME_OBJECT_REGISTRY["Field"].values():
        field_no_1 = cast(Field, field_obj)
        if field_no_1.id not in help_dict:
            help_dict[field_no_1.id] = {}

        for connector in field_no_1.connections["Edge"]._dict.values():
            if connector.id not in help_dict[field_no_1.id]:
                help_dict[field_no_1.id][connector.id] = 0
            elif help_dict[field_no_1.id][connector.id] != 0:
                continue

            if connector.obj is not None:
                direction = direction_map.get((connector.pos.y, connector.pos.x), None)
                field_no_2, connector_no_1_start, connector_no_2_end = find_next_field_in_direction(field_no_1, direction, direction_map)

                if field_no_2 is not None:
                    if connector_no_1_start is None or connector_no_2_end is None or connector_no_1_start is not connector:
                        raise ValueError("Error in finding next field in direction")
                    else:
                        if field_no_2.id not in help_dict:
                            help_dict[field_no_2.id] = {}
                        elif connector_no_2_end.id not in help_dict[field_no_2.id]:
                            help_dict[field_no_2.id][connector_no_2_end.id] = 0
                        elif connector_no_2_end.id in help_dict[field_no_2.id] and help_dict[field_no_2.id][connector_no_2_end.id] != 0:
                            continue

                        field_no_3, connector_no_2_start, connector_no_3_end = find_next_field_in_direction(
                            field_no_2, direction, direction_map
                        )

                        if field_no_3 is not None:
                            if field_no_3.id not in help_dict:
                                help_dict[field_no_3.id] = {}
                            elif connector_no_3_end.id not in help_dict[field_no_3.id]:
                                help_dict[field_no_3.id][connector_no_3_end.id] = 0
                            elif connector_no_3_end.id in help_dict[field_no_3.id] and help_dict[field_no_3.id][connector_no_3_end.id] != 0:
                                continue

                            if connector_no_2_start not in help_dict[field_no_2.id]:
                                help_dict[field_no_2.id][connector_no_2_start.id] = 0
                            elif help_dict[field_no_2.id][connector_no_2_start.id] != 0:
                                continue

                            if connector_no_2_start is None or connector_no_3_end is None:
                                raise ValueError("Error in finding next field in direction")
                            else:
                                field_no_4, _, _ = find_next_field_in_direction(field_no_3, direction, direction_map)
                                if field_no_4 is None:
                                    fc_map.overlay_ids(field_no_1.position, np.full_like(field_no_1.identifier_hitbox, curr_mill_id))
                                    fc_map.overlay_ids(field_no_2.position, np.full_like(field_no_2.identifier_hitbox, curr_mill_id))
                                    fc_map.overlay_ids(field_no_3.position, np.full_like(field_no_3.identifier_hitbox, curr_mill_id))

                                    help_dict[field_no_1.id][connector.id] = curr_mill_id
                                    help_dict[field_no_2.id][connector_no_2_end.id] = curr_mill_id
                                    help_dict[field_no_3.id][connector_no_3_end.id] = curr_mill_id
                                    help_dict[field_no_2.id][connector_no_2_start.id] = curr_mill_id

                                    curr_mill_id += 1
                                else:
                                    raise ValueError("Found 4 in a row, which should not be possible in this game")

    print(f"Created {curr_mill_id - 1} mills on the board.")
    # print(fc_map)

    save_dict = {
        "objects": game_objects_to_dict(),
        "mill_detection_hitbox": fc_map.to_dict(),
        "display_size": {"y": max_y + 1, "x": max_x + 1 + x_adjustment},
        "graphic_data_path": _TERMINAL_GRAPHICS_PATH,
    }

    # save to json
    os.makedirs("graphic_data", exist_ok=True)
    with open(f"graphic_data/board_size_{size}.json", "w") as f:
        json.dump(save_dict, f, indent=4)

    _GAME_OBJECT_REGISTRY.clear()
