import json
from typing import Any

if __name__ == "__main__":
    import sys
    from os.path import abspath, dirname

    sys.path.append(dirname(dirname(abspath(__file__))))

import numpy as np

from data_loaders import game_object_registry as gor
from data_loaders.class_registry import register_game_object_class
from data_loaders.terminal_texture import Texture
from data_loaders.texture_registry import TextureRegistry, load_textures
from game_objects.hitboxes import CoOccurrenceMap
from utils.connection_list import ConnectorList
from utils.position import Position2D
from utils.validators import PositiveInt

#


@register_game_object_class
class GameObject:
    position = Position2D()  # type: ignore
    id: int = PositiveInt()  # type: ignore

    def __init__(self, **kwargs) -> None:  # TODO add hints what to add in kwargs
        self.position = (0, 0)
        self.id = 0
        self.texture = None

        super().__init__()

        if kwargs:
            self.load(kwargs)

    def load(self, data: dict[str, Any]):
        pos_data = data.get("position", None)
        if pos_data:
            self.position = Position2D.from_dict(pos_data)

        self.id = data.get("id", 0)

        tex = data.get("texture", None)

        if tex:
            self.texture = TextureRegistry.from_dict(tex)
            self.identifier_hitbox = np.full((self.texture.height, self.texture.width), fill_value=self.id, dtype=np.uint16)

        try:
            super().load(data)
        except AttributeError:
            pass

    def update_identifier_hitbox(self):
        if self.texture and self.id != 0:
            self.identifier_hitbox = np.full((self.texture.height, self.texture.width), fill_value=self.id, dtype=np.uint16)

    def render(self):
        return self.position, self.texture

    #
    ### Json serialization methods ###
    #

    def to_dict(self) -> dict[str, Any]:
        try:
            base = dict(super().to_dict())
        except AttributeError:
            base = {}

        ### GAME OBJECT SERIALIZATION ###
        base.update(
            {
                "__type__": self.__class__.__name__,
                "id": self.id,
                "position": self.position.to_dict(),
                "texture": self.texture.to_dict() if self.texture else None,
            }
        )
        ### GAME OBJECT SERIALIZATION ###

        return base

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, s: str):
        data = json.loads(s)
        obj = cls(**data)
        return obj


#
#
#


@register_game_object_class
class Connectable:
    def __init__(self, **kwargs) -> None:
        self.connections = {}
        self.connector_hitboxes = {}

        self.hitbox_size = (0, 0)
        self.allign_offset = 0
        self.hitbox_position = None

        super().__init__()

        if kwargs:
            self.load(kwargs)

    def load(self, data: dict[str, Any]):
        self.connections.update({class_name: ConnectorList.from_dict(info) for class_name, info in data.get("connections", {}).items()})

        self.allign_offset = data.get("allign_offset", 0)

        self.hitbox_position = data.get("hitbox_position", None)
        if self.hitbox_position is None:
            self.hitbox_position = (-self.allign_offset, -self.allign_offset)
        else:
            self.hitbox_position = tuple(self.hitbox_position)

        hitbox_size_data = data.get("hitbox_size", None)

        if hitbox_size_data:
            self.hitbox_size = tuple(hitbox_size_data)

        elif hasattr(self, "identifier_hitbox"):
            y, x = self.identifier_hitbox.shape
            self.hitbox_size = (y + 2 * self.allign_offset, x + 2 * self.allign_offset)

        self.update_hitbox_map()

        if not hasattr(self, "id"):
            self.id = data.get("id", 0)

        try:
            super().load(data)
        except AttributeError:
            pass

    def update_hitbox_map(self, class_name=None):
        if class_name is not None:
            iterator = [(class_name, self.connections[class_name])]
        else:
            iterator = self.connections.items()

        for class_name, connector_list in iterator:
            if class_name not in self.connector_hitboxes:
                self.connector_hitboxes[class_name] = CoOccurrenceMap(*self.hitbox_size)
            else:
                self.connector_hitboxes[class_name].clear()

            for connector in connector_list._dict.values():
                if connector.free:
                    self.connector_hitboxes[class_name].update_hitbox(
                        (
                            connector.pos.y - self.hitbox_position[0] - connector.allign_offset,
                            connector.pos.x - self.hitbox_position[1] - connector.allign_offset,
                        ),
                        connector.identifier_hitbox,
                    )

    def try_connect(self, class_name=None):
        if class_name:
            iterator = [class_name]
        else:
            iterator = self.connections.keys()

        for class_name in iterator:
            if class_name not in self.connections:
                continue

            if isinstance(self, GameObject):
                pos_look = (
                    self.position.y + self.hitbox_position[0],
                    self.position.x + self.hitbox_position[1],
                )
            else:
                raise ValueError("Can only connect GameObjects for now")

            ignore_same_ids = class_name == self.__class__.__name__
            obj_id, _, _ = gor._GAME_OBJECT_HITBOXES[class_name].best_overlap_ids(
                pos_look, np.full_like(self.connector_hitboxes[class_name].hitbox_array, self.id), ignore_same_ids=ignore_same_ids
            )

            if obj_id != 0:
                obj = gor.resolve_game_object(class_name, obj_id)

                if isinstance(obj, GameObject):
                    pos_obj_hitbox = (
                        obj.position.y + obj.hitbox_position[0],
                        obj.position.x + obj.hitbox_position[1],
                    )
                else:
                    raise ValueError("Can only connect GameObjects for now")

                if obj is not None and isinstance(obj, Connectable):
                    obj_connector_id, my_connector_id, _ = obj.connector_hitboxes[self.class_name].best_overlap_ids(
                        (pos_look[0] - pos_obj_hitbox[0], pos_look[1] - pos_obj_hitbox[1]),
                        self.connector_hitboxes[class_name].hitbox_array,
                        ignore_same_ids=False,
                    )

                    if obj_connector_id != 0 and my_connector_id != 0:
                        obj.connections[self.class_name].connect(
                            self,
                            self.connections[class_name]._dict[my_connector_id],
                            obj_connector_id,
                        )
                        obj.update_hitbox_map(
                            self.class_name
                        )  # could be speed up by just clearing the part previously taken by the connector

                        self.connections[class_name].connect(
                            obj,
                            obj.connections[self.class_name]._dict[obj_connector_id],
                            my_connector_id,
                        )
                        self.update_hitbox_map(class_name)
                        return

        raise ValueError("Failed to connect :(")

    def disconnect(self, class_name=None, connector_id=None):
        if class_name:
            iterator = [class_name]
        else:
            iterator = self.connections.keys()

        for class_name in iterator:
            if class_name not in self.connections:
                continue

            if connector_id:
                iterator_ids = [connector_id]
            else:
                iterator_ids = self.connections[class_name]._dict.keys()

            for connector_id in iterator_ids:
                if connector_id in self.connections[class_name]._dict:
                    if self.connections[class_name]._dict[connector_id].free:
                        continue

                    self.connections[class_name]._dict[connector_id].connector.disconnect()
                    try:
                        self.connections[class_name]._dict[connector_id].obj.update_hitbox_map(self.class_name)
                    except KeyError:
                        self.connections[class_name]._dict[connector_id].obj.update_hitbox_map(self.__class__.__name__)

                    self.connections[class_name]._dict[connector_id].disconnect()
                    self.update_hitbox_map(class_name)

    def connect_after_load(self):
        for connector_list in self.connections.values():
            connector_list.connect_from_previous_load(self)

        self.update_hitbox_map()

    @property
    def class_name(self):
        return self.__class__.__name__

    #
    ### Json serialization methods ###
    #

    def to_dict(self) -> dict[str, Any]:
        try:
            base = dict(super().to_dict())  # type: ignore
        except AttributeError:
            base = {}

        ### CONNECTION SERIALIZATION ###
        connections_data = {}
        for class_name, connector_list in self.connections.items():
            connections_data[class_name] = connector_list.to_dict()

        # hitbox_data = {}
        # for class_name, hitbox_map in self.connector_hitboxes.items():
        #     hitbox_data[class_name] = hitbox_map.to_dict()
        ### CONNECTION SERIALIZATION ###

        if self.hitbox_size == (0, 0) and hasattr(self, "identifier_hitbox"):
            y, x = self.identifier_hitbox.shape
            self.hitbox_size = (y + 2 * self.allign_offset, x + 2 * self.allign_offset)

        base.update(
            {
                "connections": connections_data,
                # "connector_hitboxes": hitbox_data,
                "hitbox_size": self.hitbox_size,
                "allign_offset": self.allign_offset,
            }
        )
        return base

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, s: str):
        data = json.loads(s)
        obj = cls(**data)
        return obj


if __name__ == "__main__":
    load_textures()

    data = {
        "__type__": "GameObject",
        "id": 1,
        "position": {"y": 12, "x": 3},
        "texture": {
            "name": "pawn_player0",
            "size": [3, 6],
        },
    }

    obj = GameObject.from_dict(data)

    obj2 = GameObject.from_json(json.dumps(data))

    print(obj.render())
    print(obj.to_json())

    print("---obj2---")

    print(obj2.render())
    print(obj2.to_json())

    # ---- GameObject + Connectable tests ----
    class AObj(GameObject, Connectable):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)

        def __repr__(self):
            return f"AObj(id={self.id})"

    class BObj(GameObject, Connectable):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)

        def __repr__(self):
            return f"BObj(id={self.id})"

    TextureRegistry.register(Texture("texA", ["aaaaa", "aaaaa", "aaaaa", "aaaaa", "aaaaa"], size=(5, 5)))
    TextureRegistry.register(Texture("texB", ["bbbbb", "bbbbb", "bbbbb", "bbbbb", "bbbbb"], size=(5, 5)))

    # Create objects with textures so identifier_hitbox is available
    a = AObj.from_dict(
        {
            "id": 101,
            "position": {"y": 0, "x": 0},
            "texture": {"name": "texA", "size": [5, 5]},
        }
    )
    b = BObj.from_dict(
        {
            "id": 202,
            "position": {"y": 0, "x": 0},
            "texture": {"name": "texB", "size": [5, 5]},
        }
    )

    # Prepare connector hitbox maps
    a.hitbox_size = (7, 7)
    a.allign_offset = 1
    a.hitbox_position = (-1, -1)

    b.hitbox_size = (7, 7)
    b.allign_offset = 1
    b.hitbox_position = (-1, -1)

    # Each side holds a ConnectorList for the other class (keyed by class name)
    a.connections["BObj"] = ConnectorList(AObj.__name__)
    b.connections["AObj"] = ConnectorList(BObj.__name__)

    # Append one connector per side
    a.connections["BObj"].append(pos=(1, 1), allign_offset=1)  # id 1
    a.connections["BObj"].append(pos=(1, 2), allign_offset=1)  # id 2
    a.connections["BObj"].append(pos=(1, 3), allign_offset=1)  # id 3

    b.connections["AObj"].append(pos=(4, 4), allign_offset=1)  # id 1
    b.connections["AObj"].append(pos=(1, 4), allign_offset=1)  # id 2

    # Update the per-class connector hitbox maps (only free connectors are written)
    a.update_hitbox_map("BObj")
    b.update_hitbox_map("AObj")

    # Cross-link connectors both ways
    a_conn = a.connections["BObj"]._dict[1]
    b_conn = b.connections["AObj"]._dict[1]
    a.connections["BObj"].connect(b, b_conn, my_connector_id=1)
    b.connections["AObj"].connect(a, a_conn, my_connector_id=1)

    print("---Connectable: connected---")
    print("A->B free:", a_conn.free, "obj:", a_conn.obj, "peer_id:", a_conn.connector.id if a_conn.connector else None)
    print("B->A free:", b_conn.free, "obj:", b_conn.obj, "peer_id:", b_conn.connector.id if b_conn.connector else None)

    # Disconnect and verify
    a_conn.disconnect()
    b_conn.disconnect()
    print("---Connectable: disconnected---")
    print("A->B free:", a_conn.free, "B->A free:", b_conn.free)

    # Hitbox sizes check (maps exist and have expected shape)
    a.connector_hitboxes.setdefault("BObj", CoOccurrenceMap(*a.hitbox_size))
    b.connector_hitboxes.setdefault("AObj", CoOccurrenceMap(*b.hitbox_size))
    print("A connector hitbox shape:", a.connector_hitboxes["BObj"].hitbox_array.shape)
    print("B connector hitbox shape:", b.connector_hitboxes["AObj"].hitbox_array.shape)

    # ---- Load AObj/BObj entirely from dictionaries (including connections) ----
    # Register classes so resolve_game_object_class works inside ConnectorList.from_dict
    register_game_object_class(AObj)
    register_game_object_class(BObj)

    a_dict_full = {
        "id": 501,
        "position": {"y": 1, "x": 1},
        "texture": {"name": "texA", "size": [5, 5]},
        "hitbox_size": [11, 11],
        "allign_offset": 0,
        "connections": {
            "BObj": {
                "class_name": "BObj",
                "connector_data": {
                    1: {
                        "position": {"y": 5, "x": 5},
                        "id": 1,
                        "allign_offset": 0,
                        "obj": {"id": 602, "class_name": "BObj", "connector_id": 1},
                    }
                },
            }
        },
        # connector_hitboxes omitted on purpose; update_hitbox_map will generate them
    }

    b_dict_full = {
        "id": 602,
        "position": {"y": 2, "x": 2},
        "texture": {"name": "texB", "size": [5, 5]},
        "hitbox_size": [11, 11],
        "allign_offset": 0,
        "connections": {
            "AObj": {
                "class_name": "AObj",
                "connector_data": {
                    1: {
                        "position": {"y": 5, "x": 5},
                        "id": 1,
                        "allign_offset": 0,
                        "obj": {"id": 501, "class_name": "AObj", "connector_id": 1},
                    }
                },
            }
        },
    }

    a_loaded = AObj.from_dict(a_dict_full)
    b_loaded = BObj.from_dict(b_dict_full)

    # Verify connectors and their load metadata
    a_c = a_loaded.connections["BObj"]._dict[1]
    b_c = b_loaded.connections["AObj"]._dict[1]
    print("---Loaded connectors---")
    print("A->B obj_load:", a_c.obj_load_dict)
    print("B->A obj_load:", b_c.obj_load_dict)

    # Build hitbox maps from loaded connector positions
    a_loaded.update_hitbox_map("BObj")
    b_loaded.update_hitbox_map("AObj")
    print("A hitbox shape:", a_loaded.connector_hitboxes["BObj"].hitbox_array.shape)
    print("B hitbox shape:", b_loaded.connector_hitboxes["AObj"].hitbox_array.shape)

    # Connect using the loaded connector info
    a_loaded.connections["BObj"].connect(b_loaded, b_c, my_connector_id=1)
    b_loaded.connections["AObj"].connect(a_loaded, a_c, my_connector_id=1)
    print("---Loaded + connected---")
    print("A->B free:", a_c.free, "obj:", a_c.obj, "peer_id:", a_c.connector.id if a_c.connector else None)
    print("B->A free:", b_c.free, "obj:", b_c.obj, "peer_id:", b_c.connector.id if b_c.connector else None)

    # Roundtrip serialization to dict/JSON
    a_round = a_loaded.to_dict()
    b_round = b_loaded.to_dict()
    print("A round keys:", sorted(a_round.keys()))
    print("B round keys:", sorted(b_round.keys()))
    import json as _json

    print("A JSON size:", len(_json.dumps(a_round)))
    print("B JSON size:", len(_json.dumps(b_round)))

    print()

    print(_json.dumps(a_round, indent=2))
