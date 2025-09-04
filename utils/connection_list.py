from collections.abc import Sequence

if __name__ == "__main__":
    import sys
    from os.path import abspath, dirname

    sys.path.append(dirname(dirname(abspath(__file__))))


import numpy as np

import data_loaders.game_object_registry as gor
from utils.position import Position2D
from utils.unchangable_attribute import CannotChange

#
#


class Connector:
    pos = Position2D()

    def __init__(self, **kwargs) -> None:
        self.pos = (0, 0)
        self.id = 0
        self.allign_offset = 0

        self.obj = None
        self.connector = None

        self.obj_load_dict = None

        if kwargs:
            pos_data = kwargs.get("position", None)
            if pos_data:
                self.pos = Position2D.from_dict(pos_data)

            self.id = kwargs.get("id", 0)
            self.allign_offset = kwargs.get("allign_offset", 0)

            self.identifier_hitbox = np.full(
                (1 + 2 * self.allign_offset, 1 + 2 * self.allign_offset),
                fill_value=self.id,
                dtype=np.uint16,
            )

            # save for later to connect after loading all the objects
            self.obj_load_dict = kwargs.get("obj", None)

    def connect(self, obj, connector):
        self.obj = obj
        self.connector = connector

    def disconnect(self):
        self.obj = None
        self.connector = None

    @property
    def free(self):
        return self.obj is None and self.connector is None

    #
    # JSON
    #

    def to_dict(self):
        temp = {
            "position": self.pos.to_dict(),
            "id": self.id,
            "allign_offset": self.allign_offset,
            "obj": None,
        }
        if self.obj:
            temp["obj"] = {
                "id": self.obj.id,
                "class_name": self.obj.__class__.__name__,
                "connector_id": self.connector.id if self.connector else None,
            }
        return temp

    @classmethod
    def from_dict(cls, data):
        return cls(**data)


# change the connector interface to connect an object but also the connector of the objet for ease of use and reflect that im the board data generation


class ConnectorList(Sequence):
    _cls_owner = CannotChange()
    _dict = CannotChange()

    def __init__(self, cls_owner: str, connector_data=None) -> None:
        super().__init__()

        self._cls_owner = cls_owner

        if not connector_data:
            self._dict = {}
        else:
            self._dict = {int(id): Connector.from_dict(connector) for id, connector in connector_data.items()}

    #
    # SEQUENCE INTERFACE
    #

    def __setitem__(self, key, value):
        if value is None:
            self._dict[key].obj = None
        else:
            raise ValueError(f"Cannot set item at index {key}. Use append() or preferably append_at() instead.")

    def __getitem__(self, key):
        return self._dict[key].obj

    def __len__(self):
        return sum(connector.obj is not None for connector in self._dict.values())

    def __iter__(self):
        return iter(connector.obj for connector in self._dict.values() if connector.obj is not None)

    #
    #
    #

    def append(self, pos, allign_offset):
        _existing_ids = np.array(list(self._dict.keys()), dtype="uint16")
        free_ids = np.setdiff1d(np.arange(1, len(_existing_ids) + 2), _existing_ids)
        new_id = int(free_ids[0])

        self._dict[new_id] = Connector(id=new_id, position={"y": pos[0], "x": pos[1]}, allign_offset=allign_offset)
        return new_id

    def connect(self, obj, connector, my_connector_id):
        self._dict[my_connector_id].connect(obj, connector)

    def connect_from_previous_load(self, owner):
        for id, connector in self._dict.items():
            if connector.obj_load_dict is not None and connector.free:
                class_name = connector.obj_load_dict.get("class_name", None)
                obj_id = connector.obj_load_dict.get("id", None)
                connector_id = connector.obj_load_dict.get("connector_id", None)

                if class_name is None or obj_id is None or connector_id is None:
                    continue

                obj = gor.resolve_game_object(class_name, obj_id)

                if not hasattr(obj, "connections") or self._cls_owner not in obj.connections:
                    continue

                obj_connector = obj.connections[self._cls_owner]._dict[connector_id]

                if obj_connector.free and obj_connector.obj_load_dict is not None:
                    obj_class_name = obj_connector.obj_load_dict.get("class_name", None)
                    obj_obj_id = obj_connector.obj_load_dict.get("id", None)
                    obj_connector_id = obj_connector.obj_load_dict.get("connector_id", None)

                    if obj_class_name is None or obj_obj_id is None or obj_connector_id is None:
                        raise ValueError(f"Invalid connector load data: {obj_connector.obj_load_dict}")

                    if (
                        gor.resolve_game_object(obj_class_name, obj_obj_id) is not owner
                        or owner.connections[class_name]._dict[obj_connector_id] != connector
                    ):
                        raise ValueError(f"Connector owner class mismatch: expected {self._cls_owner}, got {type(my_owner_obj)}")

                    connector.connect(obj, obj_connector)

                    obj_connector.connect(owner, connector)

    #
    # JSON
    #

    def to_dict(self) -> dict[str, list[list[int]]]:
        return {
            "class_name": self._cls_owner,
            "connector_data": {id: connector.to_dict() for id, connector in self._dict.items()},
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data["class_name"], data["connector_data"])


#
#
#
#
#

if __name__ == "__main__":
    # New tests for the updated Connector and ConnectorList API

    class A:
        def __init__(self, id_):
            self.id = id_
            self.connections = {}

        def __repr__(self):
            return f"A({self.id})"

    class B:
        def __init__(self, id_):
            self.id = id_
            self.connections = {}

        def __repr__(self):
            return f"B({self.id})"

    # Create two objects
    a = A(1)
    b = B(2)

    # Each object has a ConnectorList for the other type
    a.connections["B"] = ConnectorList(A.__name__)
    b.connections["A"] = ConnectorList(B.__name__)

    # Append connectors (IDs start from 1 and increment)
    a.connections["B"].append(pos=(0, 0), allign_offset=0)  # A's connector id -> 1
    b.connections["A"].append(pos=(1, 1), allign_offset=1)  # B's connector id -> 1

    # Grab connectors
    a_conn = a.connections["B"]._dict[1]
    b_conn = b.connections["A"]._dict[1]

    # Connect both sides (pass the counterpart Connector)
    a.connections["B"].connect(b, b_conn, my_connector_id=1)
    b.connections["A"].connect(a, a_conn, my_connector_id=1)

    print("Connected state:")
    print("  A->B:", not a_conn.free, "obj:", a_conn.obj, "peer_id:", b_conn.id if a_conn.connector else None)
    print("  B->A:", not b_conn.free, "obj:", b_conn.obj, "peer_id:", a_conn.id if b_conn.connector else None)

    # Validate identifier hitboxes
    print("Hitboxes:")
    print("  A_conn shape:", a_conn.identifier_hitbox.shape, "values:", np.unique(a_conn.identifier_hitbox).tolist())
    print("  B_conn shape:", b_conn.identifier_hitbox.shape, "values:", np.unique(b_conn.identifier_hitbox).tolist())

    # Disconnect and verify
    a_conn.disconnect()
    b_conn.disconnect()
    print("After disconnect:")
    print("  A_conn.free:", a_conn.free, "B_conn.free:", b_conn.free)

    # Append more connectors to verify ID allocation
    a.connections["B"].append(pos=(2, 2), allign_offset=0)  # should become id 2
    b.connections["A"].append(pos=(3, 3), allign_offset=0)  # should become id 2
    print("Connector IDs now:")
    print("  A side:", sorted(a.connections["B"]._dict.keys()))
    print("  B side:", sorted(b.connections["A"]._dict.keys()))

    # ---- Serialization and loading tests ----
    # Reconnect using the second pair (id 2 on both sides)
    a_conn2 = a.connections["B"]._dict[2]
    b_conn2 = b.connections["A"]._dict[2]
    a.connections["B"].connect(b, b_conn2, my_connector_id=2)
    b.connections["A"].connect(a, a_conn2, my_connector_id=2)

    # Serialize to dict
    a_dict = a.connections["B"].to_dict()
    b_dict = b.connections["A"].to_dict()
    print("Serialized A->B keys:", list(a_dict.keys()))
    print("Serialized B->A keys:", list(b_dict.keys()))

    # Register classes for from_dict
    from data_loaders.class_registry import register_game_object_class

    register_game_object_class(A)
    register_game_object_class(B)

    # Create new owner instances and register them (simulate load into fresh objects)
    a_loaded = A(a.id)
    b_loaded = B(b.id)

    # Ensure the registry resolves to the "loaded" objects by registering them
    gor.register_game_object(a_loaded)
    gor.register_game_object(b_loaded)

    # Load lists from dict
    a_loaded.connections["B"] = ConnectorList.from_dict(a_dict)
    b_loaded.connections["A"] = ConnectorList.from_dict(b_dict)

    a_loaded.connections["B"].connect_from_previous_load(a_loaded)
    b_loaded.connections["A"].connect_from_previous_load(b_loaded)

    # Verify loaded connector fields and obj_load_dicts
    la_conn2 = a_loaded.connections["B"]._dict[2]
    lb_conn2 = b_loaded.connections["A"]._dict[2]

    print(
        "Loaded A side connector[2]: pos:",
        la_conn2.pos.to_dict() if hasattr(la_conn2.pos, "to_dict") else la_conn2.pos,
        "offset:",
        la_conn2.allign_offset,
        "obj_load:",
        la_conn2.obj_load_dict,
    )
    print(
        "Loaded B side connector[2]: pos:",
        lb_conn2.pos.to_dict() if hasattr(lb_conn2.pos, "to_dict") else lb_conn2.pos,
        "offset:",
        lb_conn2.allign_offset,
        "obj_load:",
        lb_conn2.obj_load_dict,
    )

    # Show that dicts are JSON-friendly (basic types only)
    import json

    print("JSON dump A size:", len(json.dumps(a_dict)))
    print("JSON dump B size:", len(json.dumps(b_dict)))
